import pytest
from bitarray import bitarray
from bitparse.bit_model import BitModel
from bitparse.fields import u4, u7, u8, u12, u16, u32, i8, i16, i32, b1, b8, f32, f64, UInt, Int, Bool


class SimpleUInt(BitModel):
    value: u8


class MultipleUInts(BitModel):
    a: u8
    b: u16
    c: u32


class SignedInts(BitModel):
    small: i8
    medium: i16
    large: i32


class BoolFields(BitModel):
    flag1: b1
    flag2: b1
    byte_flag: b8


class FloatFields(BitModel):
    value32: f32
    value64: f64


class MixedTypes(BitModel):
    count: u8
    enabled: b1
    _padding: u7
    _padding2: u8
    temperature: i16


class NonStandardBitSizes(BitModel):
    a: u8
    b: u12
    c: u4


def test_simple_uint_parsing():
    data = b"\x2a"
    model = SimpleUInt.from_bytes(data)
    assert model.value == 42


def test_simple_uint_unparsing():
    model = SimpleUInt(value=42)
    assert model.to_bytes() == b"\x2a"


def test_simple_uint_roundtrip():
    data = b"\xff"
    model = SimpleUInt.from_bytes(data)
    assert model.to_bytes() == data


def test_multiple_uints_parsing():
    data = b"\x01\x02\x03\x04\x05\x06\x07"
    model = MultipleUInts.from_bytes(data)
    assert model.a == 0x01
    assert model.b == 0x0203
    assert model.c == 0x04050607


def test_multiple_uints_unparsing():
    model = MultipleUInts(a=0x01, b=0x0203, c=0x04050607)
    assert model.to_bytes() == b"\x01\x02\x03\x04\x05\x06\x07"


def test_multiple_uints_roundtrip():
    data = b"\xaa\xbb\xcc\xdd\xee\xff\x00"
    model = MultipleUInts.from_bytes(data)
    assert model.to_bytes() == data


def test_signed_ints_parsing_positive():
    data = b"\x7f\x7f\xff\x7f\xff\xff\xff"
    model = SignedInts.from_bytes(data)
    assert model.small == 127
    assert model.medium == 32767
    assert model.large == 2147483647


def test_signed_ints_parsing_negative():
    data = b"\x80\x80\x00\x80\x00\x00\x00"
    model = SignedInts.from_bytes(data)
    assert model.small == -128
    assert model.medium == -32768
    assert model.large == -2147483648


def test_signed_ints_unparsing_positive():
    model = SignedInts(small=127, medium=32767, large=2147483647)
    assert model.to_bytes() == b"\x7f\x7f\xff\x7f\xff\xff\xff"


def test_signed_ints_unparsing_negative():
    model = SignedInts(small=-128, medium=-32768, large=-2147483648)
    assert model.to_bytes() == b"\x80\x80\x00\x80\x00\x00\x00"


def test_signed_ints_roundtrip():
    data = b"\xff\xfe\xfd\xfc\xfb\xfa\xf9"
    model = SignedInts.from_bytes(data)
    assert model.to_bytes() == data


def test_bool_fields_parsing():
    data = b"\x80\x40"
    model = BoolFields.from_bytes(data)
    assert model.flag1
    assert not model.flag2
    assert model.byte_flag


def test_bool_fields_unparsing():
    model = BoolFields(flag1=True, flag2=False, byte_flag=True)
    assert model.to_bytes() == b"\x80\x40"


def test_bool_fields_all_false():
    model = BoolFields(flag1=False, flag2=False, byte_flag=False)
    assert model.to_bytes() == b"\x00\x00"


def test_float_fields_parsing():
    data = b"\x42\x28\x00\x00\x40\x45\x00\x00\x00\x00\x00\x00"
    model = FloatFields.from_bytes(data)
    assert abs(model.value32 - 42.0) < 0.001
    assert abs(model.value64 - 42.0) < 0.001


def test_float_fields_unparsing():
    model = FloatFields(value32=42.0, value64=42.0)
    result = model.to_bytes()
    assert len(result) == 12
    roundtrip = FloatFields.from_bytes(result)
    assert abs(roundtrip.value32 - 42.0) < 0.001
    assert abs(roundtrip.value64 - 42.0) < 0.001


def test_mixed_types_parsing():
    data = b"\x0a\x80\x00\xfe\xd4"
    model = MixedTypes.from_bytes(data)
    assert model.count == 10
    assert model.enabled
    assert model.temperature == -300


def test_mixed_types_unparsing():
    model = MixedTypes(count=10, enabled=True, temperature=-300)
    assert model.to_bytes() == b"\x0a\x80\x00\xfe\xd4"


def test_mixed_types_roundtrip():
    data = b"\xff\x00\x00\x12\x34"
    model = MixedTypes.from_bytes(data)
    assert model.to_bytes() == data


def test_non_standard_bit_sizes_parsing():
    arr = bitarray()
    arr.frombytes(b"\xff\xff\xff")
    arr = arr[:24]
    data = arr.tobytes()
    model = NonStandardBitSizes.from_bytes(data)
    assert model.a == 0xff
    assert model.b == 0xfff
    assert model.c == 0xf


def test_non_standard_bit_sizes_unparsing():
    model = NonStandardBitSizes(a=0xff, b=0xfff, c=0xf)
    result = model.to_bytes()
    assert len(result) == 3
    arr = bitarray()
    arr.frombytes(result)
    assert arr[0:8].tobytes() == b"\xff"


def test_non_standard_bit_sizes_specific_values():
    model = NonStandardBitSizes(a=0xab, b=0xcd0, c=0xe)
    result = model.to_bytes()
    roundtrip = NonStandardBitSizes.from_bytes(result)
    assert roundtrip.a == 0xab
    assert roundtrip.b == 0xcd0
    assert roundtrip.c == 0xe


def test_bytes_conversion():
    model = SimpleUInt(value=123)
    assert bytes(model) == b"\x7b"


def test_zero_values():
    model = MultipleUInts(a=0, b=0, c=0)
    assert model.to_bytes() == b"\x00\x00\x00\x00\x00\x00\x00"


def test_max_values():
    model = MultipleUInts(a=255, b=65535, c=4294967295)
    assert model.to_bytes() == b"\xff\xff\xff\xff\xff\xff\xff"


def test_placeholder_not_in_init():
    model = MixedTypes(count=5, enabled=False, temperature=100)
    assert model.count == 5
    assert not model.enabled
    assert model.temperature == 100
    with pytest.raises(AttributeError):
        _ = model._padding
