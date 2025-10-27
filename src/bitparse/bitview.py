from collections.abc import Buffer
from inspect import BufferFlags
from typing import Literal, Self
import functools

from bitarray import bitarray
import bitarray.util as util


class bitview(Buffer):
    def __init__(self, buffer: Buffer):
        if isinstance(buffer, bitview):
            self._data = buffer._data
            self._start = buffer._start
            self._len = buffer._len
            self._step = buffer._step
        else:
            if isinstance(buffer, bitarray):
                self._data = buffer
            else:
                self._data = bitarray(buffer=buffer, endian="big")
            self._start = 0
            self._len = len(self._data)
            self._step = 1

    @functools.singledispatchmethod
    def __getitem__(self, idx: int) -> Literal[0, 1]:
        if idx < 0:
            idx += len(self)
        if not 0 <= idx < len(self):
            raise IndexError("bitview index out of range: {idx=}")
        idx = self._step * idx + self._start
        return self._data[idx]

    @__getitem__.register
    def _(self, idx: slice) -> Self:
        r = range(*idx.indices(len(self)))
        view = type(self)(self._data)
        view._start = self._start + r.start
        view._len = len(r)
        view._step = self._step * r.step
        return view

    def __len__(self) -> int:
        return self._len

    def __buffer__(self, flag: BufferFlags) -> memoryview:
        if self._step != 1:
            raise NotImplementedError("buffer interface only supported for contiguous bitviews")
        view = self._data.__buffer__(flag)
        stop = self._start + len(self) * self._step
        return view[self._start // 8 : ceildiv(stop, 8)]

    def __release_buffer__(self, buffer: memoryview):
        self._data.__release_buffer__(buffer)

    def __bytes__(self) -> bytes:
        stop = self._start + len(self) * self._step
        return self._data[self._start : stop : self._step].tobytes()

    def tobytes(self):
        return bytes(self)

    def toint(self, signed: bool = False) -> int:
        stop = self._start + len(self) * self._step
        return util.ba2int(self._data[self._start : stop : self._step], signed=signed)


def ceildiv(a: int, b: int) -> int:
    return -(-a // b)
