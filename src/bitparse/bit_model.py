import ast
from collections.abc import Buffer
from typing import Annotated, dataclass_transform, Protocol, Self
import inspect

from .bitview import bitview

type u8 = Annotated[int, UInt(bits=8)]


@dataclass_transform()
class BitMeta(type):
    def __new__(meta, name, bases, dct):
        cls = super().__new__(meta, name, bases, dct)
        print(cls, bases)
        if not bases:
            return cls
        fields = []
        args = [ast.arg(arg="self")]
        body = []
        namespace = {}
        for name, annotation in dct["__annotations__"].items():
            type_name = f"__T_for_{name}"
            namespace[type_name] = annotation
            args.append(ast.arg(arg=name, annotation=ast.Name(id=type_name, ctx=ast.Load())))
            body.append(
                ast.Assign(
                    targets=[ast.Attribute(ast.Name("self", ast.Load()), name, ast.Store())],
                    value=ast.Name(name, ast.Load())
                )
            )
        mod = ast.Module([
            ast.FunctionDef(
                name="__init__",
                args=ast.arguments(args=args),
                body=body
            )
        ])
        ast.fix_missing_locations(mod)
        code = compile(mod, filename="<dynamic>", mode="exec")
        exec(code, namespace)
        setattr(cls, "__init__", namespace["__init__"])
        print("AAA")
        print(cls)
        return cls


class BitModel(metaclass=BitMeta):
    @classmethod
    def from_bytes(cls, buffer: Buffer) -> Self:
        init_kwargs = {}
        """
        for field in self._fields:
            val, buffer = field.from_bytes(buffer, init_kwargs)
            if not field.placeholder:
                init_kwargs[field.name] = val
        """
        print(inspect.signature(cls.__init__))
        return cls(i=0, j=2, k=3)


class Field[T](Protocol):
    @classmethod
    def from_bytes(cls, buffer: bitview) -> tuple[T, bitview]: ...


class UInt:
    @classmethod
    def from_bytes(cls, buffer: bitview) -> tuple[int, bitview]:
        return int.from_bytes(buffer[:8], signed=False), buffer[8:]
