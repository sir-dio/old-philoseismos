""" philoseismos: with passion for the seismic method.

This files contains tests for Horizontally Layered Model object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import pytest

from philoseismos.models import HorizontallyLayeredModel


# @pytest.fixture(scope='module')
# def hlm():
#     model = HorizontallyLayeredModel(
#         alpha=1000,
#         beta=500,
#         rho=1300
#     )


def test_creating_hlm():
    """ Test creation of HLMs. """

    hlm = HorizontallyLayeredModel(
        alpha=1000,
        beta=500,
        rho=1300
    )

    # stores the parameters
    assert hlm.alpha == 1000
    assert hlm.beta == 500
    assert hlm.rho == 1300
