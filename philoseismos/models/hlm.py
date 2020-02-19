""" philoseismos: with passion for the seismic method.

This files defines the Horizontally Layered Model class.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

from philoseismos.models.layer import Layer


class HorizontallyLayeredModel:

    def __init__(self, alpha, beta, rho):
        """ Create a new HLM: represented by the half-space.

        To add layers on top of the half-space, use add_layer() method.

        Args:
            alpha (float): P-wave velocity in m / s.
            beta (float): S-wave velocity in m / s.
            rho (float): Density in kg / m^3.

        """

        self.alpha = alpha
        self.beta = beta
        self.rho = rho

        self._layers = []

    def add_layer(self, alpha, beta, rho, h):
        """ Add a layer on top of the HLM.

        The layers are added on top! So the model is always created from bottom to top:
        first the half-space is created (HLM object itself), then new layers are
        added on top until the model is finished.

        Args:
            alpha (float): P-wave velocity in m / s.
            beta (float): S-wave velocity in m / s.
            rho (float): Density in kg / m^3.
            h (float): Thickness in m.

        """

        layer = Layer(alpha=alpha, beta=beta, rho=rho, h=h)
        self._layers.append(layer)

    @property
    def layers(self):
        return tuple(self._layers)

    def __str__(self):
        string = ''

        for i, l in enumerate(reversed(self._layers)):
            string += f'Layer #{i}: alpha={l.alpha} beta={l.beta} rho={l.rho} h={l.h}\n'

        string += f'Half-space: alpha={self.alpha} beta={self.beta} rho={self.rho}'

        return string
