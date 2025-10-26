from collections.abc import Buffer
from inspect import BufferFlags
from typing import Literal, Self
import functools
import math

from bitarray import bitarray


class bitview(Buffer):
    def __init__(self, buffer: Buffer):
        if isinstance(buffer, bitarray):
            self._data = buffer
        elif isinstance(buffer, bitview):
            self._data = buffer._data
        else:
            self._data = bitarray(buffer=buffer, endian="big")
        self._start = 0
        self._stop = len(self._data)
        self._step = 1

    @functools.singledispatchmethod
    def __getitem__(self, idx: int) -> Literal[0, 1]:
        idx = self._abs_idx(idx)
        if not self._start <= idx < self._stop:
            raise IndexError("bitview index out of range: {idx=}")
        return self._data[idx]

    @__getitem__.register
    def _(self, idx: slice) -> Self:
        if idx.step == 0:
            raise ValueError("slice step cannot be zero")
        # Convert None values to defaults.
        start = 0 if idx.start is None else idx.start
        stop = len(self) if idx.stop is None else idx.stop
        step = 1 if idx.step is None else idx.step
        # Adjust start and stop to fall within the current subview.
        start = max(self._abs_idx(start), self._start)
        stop = min(self._abs_idx(stop), self._stop)

        view = type(self)(self._data)
        view._start = start
        view._stop = stop
        view._step = step * self._step
        return view

    def __len__(self) -> int:
        return math.ceil((self._stop - self._start) / self._step)

    def __buffer__(self, flag: BufferFlags) -> memoryview:
        if abs(self._step) != 1:
            raise NotImplementedError("buffer interface only supported for contiguous bitviews")
        view = self._data.__buffer__(flag)
        return view[self._start // 8:(self._stop + 7) // 8:self._step]

    def __release_buffer__(self, buffer: memoryview):
        self._data.__release_buffer__(buffer)

    def __bytes__(self) -> bytes:
        return self._data[self._start:self._stop:self._step].tobytes()

    def tobytes(self):
        return bytes(self)

    def _abs_idx(self, idx: int) -> int:
        """Convert the idx to be non-negative and to start from the first bit of self._data."""
        if idx < 0:
            idx += len(self)
        offset = self._start if self._step > 0 else self._stop
        return self._step * idx + offset
