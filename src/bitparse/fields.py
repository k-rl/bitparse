from dataclasses import dataclass
from typing import Annotated, Protocol

from .bitview import bitview

type u1 = Annotated[int, UInt(bits=1)]
type u8 = Annotated[int, UInt(bits=8)]


@dataclass
class Field[T](Protocol):
    placeholder: bool = False

    def from_bytes(self, buffer: bitview) -> tuple[T, bitview]: ...


@dataclass
class UInt:
    bits: int
    placeholder: bool = False

    def from_bytes(self, buffer: bitview) -> tuple[int, bitview]:
        return buffer[: self.bits].toint(signed=False), buffer[self.bits :]
