""" philoseismos: with passion for the seismic method.

This contains tests for the Layer object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import pytest
import numpy as np

from philoseismos.models.layer import Layer


def test_layer_creation():
    """ Test creation of Layers. """

    l = Layer(
        alpha=200,
        beta=100,
        rho=1500,
        h=10
    )

    assert l.alpha == 200
    assert l.beta == 100
    assert l.rho == 1500
    assert l.h == 10


@pytest.mark.parametrize("beta", [100, 200, 300])
@pytest.mark.parametrize("rho", [500, 1000, 1500])
@pytest.mark.parametrize("h", [5, 10, 15])
@pytest.mark.parametrize("w", [40, 50, 60])
@pytest.mark.parametrize("c", [50, 105, 150])
def test_layer_matrix_for_love_waves(beta, rho, h, w, c):
    """ Test the method for returning the layer matrix for Love Waves. """

    layer = Layer(
        alpha=None,
        beta=beta,
        rho=rho,
        h=h
    )

    k = w / c
    mu = rho * beta ** 2
    s = np.lib.scimath.sqrt((w / beta) ** 2 - k ** 2)
    Q = h * s

    a11 = np.cos(Q)
    a12 = np.sin(Q) / mu / s
    a21 = - mu * s * np.sin(Q)
    a22 = np.cos(Q)

    layer_matrix = layer.layer_matrix_love(omega=w, c=c)

    assert layer_matrix.shape == (2, 2)
    assert layer_matrix[0, 0] == a11
    assert layer_matrix[0, 1] == a12
    assert layer_matrix[1, 0] == a21
    assert layer_matrix[1, 1] == a22
