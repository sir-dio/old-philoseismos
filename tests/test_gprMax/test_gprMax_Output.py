""" philoseismos: with passion for the seismic method.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import pytest
import tempfile

from philoseismos.gprMax import Output


@pytest.fixture
def output():
    return Output
