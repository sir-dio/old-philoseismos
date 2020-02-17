""" philoseismos: with passion for the seismic method.

This files contains tests for Horizontally Layered Model object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import pytest
import numpy as np

from philoseismos.models import HorizontallyLayeredModel
from philoseismos.models.layer import Layer


@pytest.fixture()
def hlm():
    """ A HLM for tests. """
    model = HorizontallyLayeredModel(
        alpha=1000,
        beta=500,
        rho=1300
    )
    return model


def test_creating_hlm(hlm):
    """ Test creation of HLMs. """

    # stores the parameters
    assert hlm.alpha == 1000
    assert hlm.beta == 500
    assert hlm.rho == 1300


def test_adding_layers(hlm):
    """ Test the process of adding layers to the HLM. """

    hlm.add_layer(alpha=250, beta=100, rho=1300, h=5)

    # HLM stores layers in the layers property
    assert len(hlm.layers) == 1

    # the layers are accessible via that property
    l0 = hlm.layers[0]
    assert isinstance(l0, Layer)
    assert l0.alpha == 250
    assert l0.beta == 100
    assert l0.rho == 1300
    assert l0.h == 5

    # the attribute is read only, so the layers are only added via the method
    with pytest.raises(AttributeError):
        hlm.layers.append(Layer(100, 50, 1000, 10))

    # adding another layer works the same
    hlm.add_layer(alpha=300, beta=200, rho=1000, h=10)
    assert len(hlm.layers) == 2
    l1 = hlm.layers[-1]
    assert l1.alpha == 300
    assert l1.beta == 200
    assert l1.rho == 1000
    assert l1.h == 10


def test_printing_hlm(hlm):
    """ Test the printing of the model. """

    string = hlm.__str__()

    # with no layers, it just prints the info about the half-space
    expected = "Half-space: alpha=1000 beta=500 rho=1300"
    assert string == expected

    # with a layer, it prints the layer first, then half-space
    hlm.add_layer(alpha=1, beta=2, rho=3, h=4)
    string = hlm.__str__()
    expected = "Layer #0: alpha=1 beta=2 rho=3 h=4\n"
    expected += "Half-space: alpha=1000 beta=500 rho=1300"
    assert string == expected

    # with multiple layers, they are listed top to bottom
    hlm.add_layer(alpha=5, beta=6, rho=7, h=8)
    string = hlm.__str__()
    expected = "Layer #0: alpha=5 beta=6 rho=7 h=8\n"
    expected += "Layer #1: alpha=1 beta=2 rho=3 h=4\n"
    expected += "Half-space: alpha=1000 beta=500 rho=1300"
    assert string == expected


def test_min_beta(hlm):
    """ Test that min_beta property returns minimal beta of all layers. """

    assert hlm.min_beta == 500

    hlm.add_layer(alpha=10, beta=5, rho=20, h=3)
    assert hlm.min_beta == 5

    hlm.add_layer(alpha=10, beta=8, rho=20, h=3)
    assert hlm.min_beta == 5

    hlm.add_layer(alpha=10, beta=3, rho=20, h=3)
    assert hlm.min_beta == 3


def test_frequency_axis_assigning(hlm):
    """ Test functionality of assigning a frequency axis for dispersion curves. """

    # raw model does not have a frequency axis
    assert hlm.fs is None
    assert hlm.omegas is None

    # the frequency is assigned via the special method
    fs = np.arange(1, 10, 2)
    hlm.set_frequency_axis(fs)

    # when its assigned, both fs and omegas are changed
    assert np.alltrue(hlm.fs == fs)
    assert np.alltrue(hlm.omegas == fs * 2 * np.pi)
