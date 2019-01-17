from philoseismos import Segy

import pytest
import numpy as np


def test_creating_raises_ValueError_when_bad_shaped_matrix_is_passed():
    with pytest.raises(ValueError):
        Segy.create_from_DataMatrix(np.empty(10))
    with pytest.raises(ValueError):
        Segy.create_from_DataMatrix(np.empty((3, 3, 3)))


@pytest.fixture(scope="module")
def segy():
    data = np.ones((10, 20), dtype=np.float32)
    data[9] *= 9
    segy = Segy.create_from_DataMatrix(data, sample_interval=500)
    return segy


def test_BFH_values_are_correct(segy):
    table = segy.BFH.table
    assert table['Sample interval'] == 500
    assert table['Sample format'] == 5
    assert table['Samples / trace'] == 20
    assert table['# Traces'] == 10
    assert table['Data offset'] == 3600


def test_Data_parameters_are_restored_correctly(segy):
    assert segy.Data.num_traces == 10
    assert segy.Data.sample_size == 4


def test_Traces_get_correct_values(segy):
    assert np.all(segy.Data.Traces[0].ys == 1)
    assert np.all(segy.Data.Traces[9].ys == 9)
