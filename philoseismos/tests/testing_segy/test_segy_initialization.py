from philoseismos import Segy

import pytest


@pytest.fixture
def segy():
    """ An empty Segy object. """
    return Segy()


def test_Segy_object_initializes_correctly(segy):
    assert segy.file == 'None'
    assert segy.endian == '>'
    assert segy.fsf is None
    assert segy.silent is False


def test_byteSegy_object_initializes_correctly(segy):
    bs = segy._byteSegy
    assert bs.segy is segy
    assert bs.tfh == bytearray()
    assert bs.bfh == bytearray()
    assert bs.data == bytearray()
    assert bs.sizeB == bs.sizeMB == 0


def test_TFH_object_initializes_correctly(segy):
    tfh = segy.TFH
    assert tfh._segy is segy
    assert tfh._whole.isspace() and len(tfh._whole) == 3200


def test_BFH_object_initializes_correctly(segy):
    bfh = segy.BFH
    assert bfh._segy is segy


def test_Data_object_initializes_correctly(segy):
    data = segy.Data
    assert data._segy is segy
    assert data.Traces == list()
