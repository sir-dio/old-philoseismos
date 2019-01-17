from philoseismos.segy.tools import ibm

import struct

# ===================== #
# ===== IBM tests ===== #


def test_ibm_unpacks_correctly():
    # IBM value of -118.625:
    value = 0b11000010011101101010000000000000
    packed = struct.pack('>L', value)
    unpacked = ibm.unpack_ibm32(packed, endian='>')
    assert unpacked == -118.625


def test_ibm_packs_correctly():
    value = -118.625
    packed = ibm.pack_ibm32(value, endian='>')
    assert packed == b'\xc2v\xa0\x00'
