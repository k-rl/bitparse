from dataclasses import dataclass
from typing import Annotated, Any, Protocol

from bitarray import bitarray
import bitarray.util as util

from .bitview import bitview

type u1 = Annotated[int, UInt(bits=1)]
type u8 = Annotated[int, UInt(bits=8)]
type i4 = Annotated[int, Int(bits=4)]
type i8 = Annotated[int, Int(bits=4)]


@dataclass
class Field[T](Protocol):
    placeholder: bool = False

    def from_bytes(self, buffer: bitview) -> tuple[T, bitview]: ...
    def to_bits(self, val: Any) -> bitarray: ...


@dataclass
class UInt:
    bits: int
    placeholder: bool = False

    def from_bytes(self, buffer: bitview) -> tuple[int, bitview]:
        return buffer[: self.bits].toint(signed=False), buffer[self.bits :]

    def to_bits(self, val: int) -> bitarray:
        return util.int2ba(val, length=self.bits, signed=False)


@dataclass
class Int:
    bits: int
    placeholder: bool = False

    def from_bytes(self, buffer: bitview) -> tuple[int, bitview]:
        return buffer[: self.bits].to_int(signed=True), buffer[self.bits :]

    def to_bits(self, val: int) -> bitarray:
        return util.int2ba(val, length=self.bits, signed=True)
