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
        h=10,
        Q=100
    )

    # when created, layers save the parameters
    assert l.alpha == 200
    assert l.beta == 100
    assert l.rho == 1500
    assert l.h == 10
    assert l.Q == 100

    # should not allow creating layers where beta > alpha
    with pytest.raises(ValueError):
        l = Layer(alpha=100, beta=200, rho=1000, h=5)


@pytest.mark.parametrize("beta", [50, 150])
@pytest.mark.parametrize("rho", [500, 1500])
@pytest.mark.parametrize("h", [5, 15])
@pytest.mark.parametrize("w", [1, 60])
@pytest.mark.parametrize("c", [50, 200])
def test_layer_matrix_for_love_waves(beta, rho, h, w, c):
    """ Test the method for returning the layer matrix for Love Waves. """

    layer = Layer(
        alpha=None,
        beta=beta,
        rho=rho,
        h=h
    )

    # formulas from Oldrich Novotny -- Seismic Surface Waves
    k = w / c
    mu = rho * beta ** 2
    s = np.lib.scimath.sqrt((w / beta) ** 2 - k ** 2)
    Q = h * s

    a11 = np.cos(Q)

    if c == beta:
        a12 = 0
    else:
        a12 = np.sin(Q) / mu / s

    a21 = - mu * s * np.sin(Q)
    a22 = np.cos(Q)

    layer_matrix = layer.layer_matrix_love(omega=w, c=c)

    assert layer_matrix.shape == (2, 2)
    assert layer_matrix[0, 0] == a11
    assert layer_matrix[0, 1] == a12
    assert layer_matrix[1, 0] == a21
    assert layer_matrix[1, 1] == a22


@pytest.mark.parametrize("alpha", [500])
@pytest.mark.parametrize("beta", [50, 150])
@pytest.mark.parametrize("rho", [500, 1500])
@pytest.mark.parametrize("h", [5, 15])
@pytest.mark.parametrize("w", [1, 60])
@pytest.mark.parametrize("c", [50, 600])
def test_layer_matrix_for_rayleigh_waves(alpha, beta, rho, h, w, c):
    """ Test the method for returning the layer matrix for Rayleigh Waves. """

    layer = Layer(
        alpha=alpha,
        beta=beta,
        rho=rho,
        h=h
    )

    # formulas from Oldrich Novotny -- Seismic Surface Waves
    k = w / c
    r = np.lib.scimath.sqrt((c / alpha) ** 2 - 1)
    s = np.lib.scimath.sqrt((c / beta) ** 2 - 1)
    gamma = 2 * (beta / c) ** 2
    delta = gamma - 1
    P = k * r * h
    Q = k * s * h

    a11 = a44 = gamma * np.cos(P) - delta * np.cos(Q)

    if c == alpha:
        a12 = a34 = gamma * s * np.sin(Q)
        a14 = s * np.sin(Q) / rho
        a32 = rho * gamma ** 2 * s * np.sin(Q)
    else:
        a12 = a34 = delta / r * np.sin(P) + gamma * s * np.sin(Q)
        a14 = (np.sin(P) / r + s * np.sin(Q)) / rho
        a32 = rho * (delta ** 2 / r * np.sin(P) + gamma ** 2 * s * np.sin(Q))

    if c == beta:
        a21 = a43 = gamma * r * np.sin(P)
        a23 = -r * np.sin(P) / rho
        a41 = -rho * gamma ** 2 * r * np.sin(P)
    else:
        a21 = a43 = gamma * r * np.sin(P) + delta / s * np.sin(Q)
        a23 = -(r * np.sin(P) + np.sin(Q) / s) / rho
        a41 = -rho * (gamma ** 2 * r * np.sin(P) + delta ** 2 / s * np.sin(Q))

    a13 = a24 = -(np.cos(P) - np.cos(Q)) / rho
    a22 = a33 = -delta * np.cos(P) + gamma * np.cos(Q)
    a31 = a42 = rho * gamma * delta * (np.cos(P) - np.cos(Q))

    layer_matrix = layer.layer_matrix_rayleigh(w, c)

    assert layer_matrix.shape == (4, 4)
    assert layer_matrix[0, 0] == a11
    assert layer_matrix[0, 1] == a12
    assert layer_matrix[0, 2] == a13
    assert layer_matrix[0, 3] == a14
    assert layer_matrix[1, 0] == a21
    assert layer_matrix[1, 1] == a22
    assert layer_matrix[1, 2] == a23
    assert layer_matrix[1, 3] == a24
    assert layer_matrix[2, 0] == a31
    assert layer_matrix[2, 1] == a32
    assert layer_matrix[2, 2] == a33
    assert layer_matrix[2, 3] == a34
    assert layer_matrix[3, 0] == a41
    assert layer_matrix[3, 1] == a42
    assert layer_matrix[3, 2] == a43
    assert layer_matrix[3, 3] == a44


def test_layer_parameter_lines():
    """ Test the parameter_lines method. """

    l = Layer(100, 50, 1000, h=5)
    a, b, r, q = l.parameter_lines(dz=1)

    # returns constant curves, not including the last point
    assert np.alltrue(a == np.array([100] * 5))
    assert np.alltrue(b == np.array([50] * 5))
    assert np.alltrue(r == np.array([1000] * 5))
    assert np.alltrue(q == 0)
