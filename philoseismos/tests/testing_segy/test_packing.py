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


# ====================== #
# ===== Data tests ===== #
