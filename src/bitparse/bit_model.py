import ast
import copy
import typing
from collections.abc import Buffer
from typing import dataclass_transform, Self

from bitarray import bitarray

from .bitview import bitview
from .fields import Field


@dataclass_transform()
class BitMeta(type):
    def __new__(meta, name, bases, dct):
        cls = super().__new__(meta, name, bases, dct)
        print(dct)
        if not bases:
            return cls

        cls.fields = {}
        args = [ast.arg(arg="self")]
        body = []
        namespace = {}
        for name, annotation in dct["__annotations__"].items():
            py_type, field = typing.get_args(annotation.__value__)
            field = copy.copy(field)
            if name.startswith("_"):
                field.placeholder = True
            type_name = f"__T_for_{name}"
            namespace[type_name] = py_type
            if not field.placeholder:
                args.append(ast.arg(arg=name, annotation=ast.Name(id=type_name, ctx=ast.Load())))
                body.append(
                    ast.Assign(
                        targets=[ast.Attribute(ast.Name("self", ast.Load()), name, ast.Store())],
                        value=ast.Name(name, ast.Load()),
                    )
                )
            cls.fields[name] = field
        mod = ast.Module(
            [
                ast.FunctionDef(
                    name="__init__",
                    args=ast.arguments(
                        posonlyargs=[], args=args, kwonlyargs=[], kw_defaults=[], defaults=[]
                    ),
                    body=body,
                    decorator_list=[],
                    type_params=[],
                )
            ],
            type_ignores=[],
        )
        ast.fix_missing_locations(mod)
        code = compile(mod, filename="<dynamic>", mode="exec")
        exec(code, namespace)
        setattr(cls, "__init__", namespace["__init__"])
        return cls


class BitModel(metaclass=BitMeta):
    fields: dict[str, Field] = {}

    @classmethod
    def from_bytes(cls, buffer: Buffer) -> Self:
        buffer = bitview(buffer)
        init_kwargs = {}
        for name, field in cls.fields.items():
            val, buffer = field.from_bytes(buffer)
            if not field.placeholder:
                init_kwargs[name] = val
        return cls(**init_kwargs)

    def to_bytes(self) -> bytes:
        arr = bitarray()
        for name, field in self.fields.items():
            if field.placeholder:
                val = 0
            else:
                val = getattr(self, name)
            arr.extend(field.to_bits(val))
        return arr.tobytes()

    def __bytes__(self) -> bytes:
        return self.to_bytes()
