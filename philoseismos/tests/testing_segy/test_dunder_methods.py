from philoseismos import Segy

import pytest
import numpy as np


@pytest.fixture(scope='module')
def segy():
    data = np.ones((5, 15))
    segy = Segy.create_from_DataMatrix(data, 500)
    return segy

# ====================== #
# ===== Segy tests ===== #


def test_Segy_repr_method(segy):
    assert segy.__repr__() == 'Segy(file=None)'
    segy.file = 'test.sgy'
    assert segy.__repr__() == 'Segy(file=test.sgy)'
