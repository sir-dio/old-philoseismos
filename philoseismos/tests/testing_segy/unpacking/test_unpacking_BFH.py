from philoseismos import Segy
from philoseismos.segy.tools.constants import bfh_string

import pytest
import struct


@pytest.fixture(scope="module")
def segy():
    sgy = Segy()
    bytearray_ = bytearray(3200)
    bytearray_ += struct.pack('>' + bfh_string, *[i for i in range(111)])
    bytearray_ += bytearray(100)
    sgy._byteSegy._load_from_bytearray(bytearray_)
    return sgy


def test_BFH_unpacks_correctly(segy):
    bfh = segy.BFH
    bfh._unpack_from_byteSegy()
    assert bfh._table.size == 111
    assert bfh._table.iloc[0] == 0
    assert bfh._table.iloc[69] == 69
    assert bfh._table.iloc[-1] == 110
