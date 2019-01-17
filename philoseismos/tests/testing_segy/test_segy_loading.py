from philoseismos import Segy

import pytest
import struct


@pytest.fixture(scope="module")
def segy():
    """ A hand-made bytearray that represents segy file. """

    tfh = bytearray('Dummy Textual Header'.ljust(3200), 'cp500')

    bfh = bytearray(400)
    bfh[16:18] = struct.pack('>h', 500)
    bfh[20:22] = struct.pack('>h', 1024)
    bfh[24:26] = struct.pack('>h', 5)

    data = bytearray(5000)  # empty data

    bytearray_ = tfh + bfh + data

    segy = Segy()
    segy._byteSegy._load_from_bytearray(bytearray_)
    segy.TFH._unpack_from_bytearray(segy._byteSegy.tfh)

    return segy


def test_TFH_loads_correctly(segy):
    assert segy.TFH._whole == 'Dummy Textual Header'.ljust(3200)


def test_endiannes_is_detected_correctly():
    pass
