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
    hlm.add_layer(alpha=2, beta=1, rho=3, h=4)
    string = hlm.__str__()
    expected = "Layer #0: alpha=2 beta=1 rho=3 h=4\n"
    expected += "Half-space: alpha=1000 beta=500 rho=1300"
    assert string == expected

    # with multiple layers, they are listed top to bottom
    hlm.add_layer(alpha=6, beta=5, rho=7, h=8)
    string = hlm.__str__()
    expected = "Layer #0: alpha=6 beta=5 rho=7 h=8\n"
    expected += "Layer #1: alpha=2 beta=1 rho=3 h=4\n"
    expected += "Half-space: alpha=1000 beta=500 rho=1300"
    assert string == expected


def test_hlm_min_max_beta_properties(hlm):
    """ Test that min_beta and max_beta properties return minimal and maximal beta of all layers. """

    # min and max beta
    assert hlm.min_beta == 500
    assert hlm.max_beta == 500

    hlm.add_layer(alpha=10, beta=5, rho=20, h=3)
    assert hlm.min_beta == 5
    assert hlm.max_beta == 500

    hlm.add_layer(alpha=700, beta=650, rho=20, h=3)
    assert hlm.min_beta == 5
    assert hlm.max_beta == 650

    hlm.add_layer(alpha=10, beta=3, rho=20, h=3)
    assert hlm.min_beta == 3
    assert hlm.max_beta == 650


def test_hlm_cumulative_layer_thickness(hlm):
    """ Test that cumulative_layer_h property returns cumulative layer thickness. """

    # for no layers
    assert hlm.cumulative_layer_h == 0

    hlm.add_layer(0, 0, 0, h=5)
    assert hlm.cumulative_layer_h == 5

    hlm.add_layer(0, 0, 0, h=250)
    assert hlm.cumulative_layer_h == 255

    hlm.add_layer(0, 0, 0, 0.15)
    assert hlm.cumulative_layer_h == 255.15


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


def test_hlm_custom_parameter_curves():
    """ Test method for creating parameter curves for custom depth curves. """

    # just the half-space
    hlm = HorizontallyLayeredModel(alpha=100, beta=50, rho=1000)
    depths, alphas, betas, rhos = hlm.parameter_profiles_for_z(z0=0, z1=10, dz=1)

    # the depth range should be inclusive
    assert np.alltrue(depths == np.arange(0, 11, 1))

    # shape of the resulting parameter curves is determined by z
    assert alphas.shape == betas.shape == rhos.shape == (11,)

    # with no layers, all the values correspond to half-space itself
    assert np.alltrue(alphas == 100)
    assert np.alltrue(betas == 50)
    assert np.alltrue(rhos == 1000)

    # add a layer
    hlm.add_layer(alpha=50, beta=25, rho=500, h=10)
    depths, alphas, betas, rhos = hlm.parameter_profiles_for_z(z0=0, z1=20, dz=5)

    # now the curves correspond to both the layer and the half-space
    assert np.alltrue(alphas == np.array([50, 50, 100, 100, 100]))
    assert np.alltrue(betas == np.array([25, 25, 50, 50, 50]))
    assert np.alltrue(rhos == np.array([500, 500, 1000, 1000, 1000]))


@pytest.mark.skip(reason="WIP")
def test_dispersion_curve_calculation(hlm):
    """ Test the method for calculating dispersion curves. """

    # TODO: come up with a way to test this

    pass
