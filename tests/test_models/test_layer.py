""" philoseismos: with passion for the seismic method.

This contains tests for the Layer object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

from philoseismos.models.layer import Layer

def test_layer_creation():
    """ Test creation of Layers. """

    l = Layer(
        alpha=200,
        beta=100,
        rho=1500,
        h=10
    )
