from philoseismos import Segy

import pytest
import numpy as np

# ========================== #
# ===== byteSegy tests ===== #


@pytest.fixture
def byteSegy():
    """ A Textual File Header of an empty Segy """
    return Segy()._byteSegy


def test_byteSegy_divides_bytearray_into_parts_correctly(byteSegy):
    tfh = bytearray([1 for i in range(3200)])
    bfh = bytearray([2 for i in range(400)])
    data = bytearray([3 for i in range(1500)])

    byteSegy._load_from_bytearray(tfh + bfh + data)

    assert byteSegy.tfh == bytearray([1 for i in range(3200)])
    assert byteSegy.bfh == bytearray([2 for i in range(400)])
    assert byteSegy.data == bytearray([3 for i in range(1500)])

# ===================================== #
# ===== Textual File Header tests ===== #


@pytest.fixture
def tfh():
    """ A Textual File Header of an empty Segy """
    return Segy().TFH


def test_TFH_raises_ValueError_when_unpacking_short_bytearray(tfh):
    with pytest.raises(ValueError):
        tfh._unpack_from_bytearray(bytearray(10))


def test_TFH_unpacks_empty_bytearray_as_spaces(tfh):
    tfh._unpack_from_bytearray(bytearray(3200))
    assert tfh._whole.isspace()


def test_TFH_unpacks_bytearray_correctly(tfh):
    bytearray_ = 'Dummy Text Header'.ljust(3200).encode('cp500')
    tfh._unpack_from_bytearray(bytearray_)
    assert tfh._whole == 'Dummy Text Header'.ljust(3200)

# ==================================== #
# ===== Binary File Header tests ===== #


@pytest.fixture
def bfh():
    """ A Binary File Header of an empty Segy """
    return Segy().BFH


def test_BFH_raises_ValueError_when_unpacking_short_bytearray(bfh):
    with pytest.raises(ValueError):
        bfh._unpack_from_bytearray(bytearray(10))


def test_BFH_unpacks_bytearray_correctly(bfh):
    bytearray_ = bytearray(400)

    bytearray_[0:4] = b'\x00\x00\x02\x9a'
    bytearray_[16:18] = b'\x01\xf4'
    bytearray_[24:26] = b'\x00\x05'
    bytearray_[320:328] = b'\x00\x00\x00\x00\x00\x01\xe2@'

    bfh._unpack_from_bytearray(bytearray_)
    assert bfh.table['Job ID'] == 666
    assert bfh.table['Sample Interval'] == 500
    assert bfh.table['Sample Format'] == 5
    assert bfh.table['Data Offset'] == 123456

# ====================== #
# ===== Data tests ===== #


@pytest.fixture
def data():
    """ A Textual File Header of an empty Segy """
    return Segy().Data


def test_Data_method_for_getting_unpacking_parameters_from_BFH(bfh, data):
    bytearray_ = bytearray(400)
    bytearray_[20:22] = b'\x04\x00'
    bytearray_[24:26] = b'\x00\x05'
    bfh._unpack_from_bytearray(bytearray_)

    params = data._get_unpacking_parameters_from_BFH(BFH=bfh)
    assert params.get('sample_format') == 5
    assert params.get('trace_length') == 1024


def test_DataMatrix_has_correct_shape(data):
    bytearray_ = bytearray(86720)
    data._unpack_from_bytearray(bytearray_, sample_format=5, trace_length=1024)
    assert data.DM.shape == (20, 1024)


def test_geometry_table_is_filled_correctly(data):
    bytearray_ = bytearray(240 + 10 * 4)
    bytearray_[20:24] = b'\x00\x0009'

    data._unpack_from_bytearray(bytearray_, sample_format=5, trace_length=10)
    assert data.geometry.at[1, 'CDP'] == 12345


def test_Trace_values_unpack_correctly(data):
    bytearray_ = bytearray((240 + 10 * 4) * 10)
    bytearray_[240:280] = b'\xc2\xed@\x00' * 10
    bytearray_[1360:1400] = b'B\xed@\x00' * 10
    bytearray_[2760:2800] = b'D\x1cG\x8d' * 10

    data._unpack_from_bytearray(bytearray_, sample_format=5, trace_length=10)
    assert np.alltrue(data.Traces[0].ys == -118.625)
    assert np.alltrue(data.Traces[4].ys == 118.625)
    assert np.alltrue(data.Traces[9].ys == 625.118)

# ========================= #
# ===== Special cases ===== #


def test_forced_sample_format_overrides_unpacked_value():
    segy = Segy(fsf=1)
    bytearray_ = bytearray(400)
    bytearray_[24:26] = b'\x00\x05'
    segy.BFH._unpack_from_bytearray(bytearray_)
    assert segy.BFH.table['Sample Format'] == 1
