from philoseismos import Segy

import pytest


@pytest.fixture(scope="module")
def segy():
    sgy = Segy()
    bytearray_ = bytearray(3200 + 400 + 100)
    sgy._byteSegy._load_from_bytearray(bytearray_)
    return sgy


def test_TFH_unpacks_empty_bytearray_as_spaces(segy):
    tfh = segy.TFH
    tfh._unpack_from_byteSegy()
    assert tfh._whole.isspace()


def test_TFH_unpacks_from_byteSegy_correctly(segy):
    segy._byteSegy.tfh = 'Dummy Text Header'.ljust(3200).encode('cp500')
    tfh = segy.TFH
    tfh._unpack_from_byteSegy()
    assert tfh._whole == 'Dummy Text Header'.ljust(3200)
