from philoseismos import Segy

import pytest
import numpy as np


@pytest.fixture(scope="module")
def TFH():
    data = np.ones((5, 10))
    segy = Segy.create_from_DataMatrix(data, 500)
    segy.TFH._whole = ''.join([f'{i:80}' for i in range(40)])
    return segy.TFH


def test_get_line_helper_method(TFH):
    assert len(TFH._get_line(0)) == 80
    assert TFH._get_line(21)[-2:] == '21'


def test_empty_method(TFH):
    TFH.empty()
    assert TFH._whole.isspace()


def test_change_line_method(TFH):
    text1 = 'This is text is on line 20'
    text2 = 'abcdefg' * 20
    TFH.change_line(20, text1)
    TFH.change_line(21, text2)
    assert TFH._get_line(19) == text1.ljust(80)
    assert TFH._get_line(20) == text2[:80]
