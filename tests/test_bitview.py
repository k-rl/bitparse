import pytest

from bitarray import bitarray
from bitparse import bitview


def test_empty_bitview():
    arr = bitarray()
    view = bitview(arr)
    assert len(view) == 0
    assert view.tobytes() == b""


def test_init_from_bitarray():
    arr = bitarray("10110010")
    view = bitview(arr)
    assert len(view) == 8
    for i, b in enumerate(arr):
        assert view[i] == b


def test_init_from_bytes():
    data = b"\xB2"
    view = bitview(data)
    assert len(view) == 8
    for i, b in enumerate(map(int, "10110010")):
        assert view[i] == b


def test_init_from_bytearray():
    data = bytearray(b"\xFF\x00")
    view = bitview(data)
    assert len(view) == 16
    for i in range(8):
        assert view[i] == 1
    for i in range(8, 16):
        assert view[i] == 0


def test_init_from_bitview():
    arr = bitarray("11001100")
    view1 = bitview(arr)
    view2 = bitview(view1)
    assert len(view2) == 8
    assert view2._data is view1._data
    for i, b in enumerate(arr):
        assert view2[i] == b


def test_getitem_negative_index():
    arr = bitarray("10110010")
    view = bitview(arr)
    for i, b in enumerate(arr):
        assert view[-len(arr) + i] == b


def test_getitem_out_of_range():
    arr = bitarray("10110010")
    view = bitview(arr)
    with pytest.raises(IndexError):
        _ = view[8]
    with pytest.raises(IndexError):
        _ = view[-9]


def test_slice_basic():
    arr = bitarray("10110010")
    view = bitview(arr)[2:6]
    assert len(view) == 4
    assert view[0] == 1
    assert view[1] == 1
    assert view[2] == 0
    assert view[3] == 0
    assert view[-4] == 1
    assert view[-3] == 1
    assert view[-2] == 0
    assert view[-1] == 0


def test_slice_with_step():
    arr = bitarray("10110010")
    view = bitview(arr)[::2]
    assert len(view) == 4
    assert view[0] == 1
    assert view[1] == 1
    assert view[2] == 0
    assert view[3] == 1


def test_slice_negative_indices():
    arr = bitarray("10110010")
    view = bitview(arr)[-4:-1]
    assert len(view) == 3
    assert view[0] == 0
    assert view[1] == 0
    assert view[2] == 1


def test_slice_with_none():
    arr = bitarray("10110010")
    view = bitview(arr)[:]
    assert len(view) == 8
    view2 = bitview(arr)[2:]
    assert len(view2) == 6
    view3 = bitview(arr)[:5]
    assert len(view3) == 5


def test_slice_nested():
    arr = bitarray("10110010")
    view1 = bitview(arr)[1:7]
    view2 = view1[1:4]
    assert len(view2) == 3
    assert view2[0] == 1
    assert view2[1] == 1
    assert view2[2] == 0


def test_slice_zero_step_raises():
    arr = bitarray("10110010")
    view = bitview(arr)
    with pytest.raises(ValueError):
        _ = view[::0]


def test_len_with_step():
    arr = bitarray("10110010")
    view = bitview(arr)[::2]
    assert len(view) == 4
    view2 = bitview(arr)[::3]
    assert len(view2) == 3


def test_tobytes_full_view():
    data = b"\xB2\xFF"
    view = bitview(data)
    assert view.tobytes() == b"\xB2\xFF"


def test_tobytes_sliced_view():
    arr = bitarray("1011001011110000")
    view = bitview(arr)[0:8]
    assert view.tobytes() == b"\xB2"
    view = bitview(arr)[2:5]
    assert view.tobytes() == b"\xC0"
    view = bitview(arr)[3:10]
    assert view.tobytes() == b"\x96"
    view = bitview(arr)[3:14]
    assert view.tobytes() == b"\x97\x80"


def test_bytes_conversion():
    data = b"\xAB\xCD"
    view = bitview(data)
    assert bytes(view) == b"\xAB\xCD"


def test_buffer_interface_contiguous():
    data = b"\xFF\x00\xAA"
    view = bitview(data)
    mv = memoryview(view)
    assert bytes(mv) == b"\xFF\x00\xAA"


def test_buffer_interface_with_slice():
    data = b"\xFF\xCC\xBB\xAA"
    view = bitview(data)
    mv = memoryview(view[8:24])
    assert bytes(mv) == b"\xCC\xBB"
    mv = memoryview(view[9:23])
    assert bytes(mv) == b"\xCC\xBB"


def test_buffer_interface_non_contiguous_raises():
    data = b"\xFF\x00\xAA"
    view = bitview(data)[::2]
    with pytest.raises(NotImplementedError):
        _ = memoryview(view)


def test_abs_idx():
    arr = bitarray("10110010")
    view = bitview(arr)
    assert view._abs_idx(0) == 0
    assert view._abs_idx(3) == 3
    assert view._abs_idx(7) == 7
    assert view._abs_idx(-1) == 7
    assert view._abs_idx(-8) == 0


def test_abs_idx_on_sliced_view():
    arr = bitarray("10110010")
    view = bitview(arr)[2:6]
    assert view._abs_idx(0) == 2
    assert view._abs_idx(3) == 5
    assert view._abs_idx(-1) == 5
    assert view._abs_idx(-3) == 3


def test_single_bit_slice():
    arr = bitarray("10110010")
    view = bitview(arr)[3:4]
    assert len(view) == 1
    assert view[0] == 1
    assert view[-1] == 1


def test_empty_slice():
    arr = bitarray("10110010")
    view = bitview(arr)[3:3]
    assert len(view) == 0


def test_complex_nested_slicing():
    arr = bitarray("1011001011110000")
    view1 = bitview(arr)[2:14]
    view2 = view1[1:10]
    view3 = view2[::2]
    view4 = view3[1::2]
    assert len(view3) == 5
    assert view3[0] == arr[3]
    assert view3[1] == arr[5]
    assert len(view4) == 2
    assert view4[0] == arr[7]
    assert view4[1] == arr[11]
    assert view4[-2] == arr[7]
    assert view4[-1] == arr[11]
