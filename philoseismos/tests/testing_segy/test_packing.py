from philoseismos import Segy

import pytest
import struct
import numpy as np


@pytest.fixture
def segy():
    data = np.ones((10, 20), dtype=np.float32)
    sgy = Segy.create_from_DataMatrix(data, sample_interval=500)
    sgy.TFH.change_line(1, "This line is changed")
    return sgy

# ========================== #
# ===== byteSegy tests ===== #


# ===================================== #
# ===== Textual File Header tests ===== #

def test_TFH_packs_correctly(segy):
    tfh = segy.TFH
    packed = tfh._pack_to_bytearray()
    assert len(packed) == 3200
    assert packed == 'This line is changed'.ljust(3200).encode('cp500')

# ==================================== #
# ===== Binary File Header tests ===== #


def test_BFH_packs_correctly(segy):
    bfh = segy.BFH
    bfh.table["Job ID"] = 65
    packed = bfh._pack_to_bytearray()
    assert len(packed) == 400
    assert packed[:4] == struct.pack('>i', 65)
    assert packed[16:18] == struct.pack('>h', 500)
    assert packed[24:26] == struct.pack('>h', 5)
    assert packed[312:320] == struct.pack('>Q', 10)
    assert packed[320:328] == struct.pack('>Q', 3600)

# ====================== #
# ===== Data tests ===== #
