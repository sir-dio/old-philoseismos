""" philoseismos: with passion for the seismic method.

This files defines the Horizontally Layered Model class.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import numpy as np
from scipy import optimize

from philoseismos.models.layer import Layer


class HorizontallyLayeredModel:

    def __init__(self, alpha, beta, rho):
        """ Create a new HLM: represented by the half-space.

        To add layers on top of the half-space, use add_layer() method.

        """

        self.alpha = alpha
        self.beta = beta
        self.rho = rho

        self._layers = []
        self._love_dispersion_curves = []

    def add_layer(self, alpha, beta, rho, h):
        """ Add a layer on top of the HLM. """

        layer = Layer(alpha=alpha, beta=beta, rho=rho, h=h)
        self._layers.append(layer)

    @property
    def layers(self):
        return tuple(self._layers)

    @property
    def min_beta(self):
        betas = [l.beta for l in self._layers]
        betas.append(self.beta)
        return min(betas)

    def _matrix_for_stack_of_layers_for_love(self, w, c):
        """ Calculate the matrix for stack of layers. """

        A = np.identity(2)

        for layer in reversed(self._layers):
            A = np.matmul(A, layer.layer_matrix_love(w, c))

        return A

    def _love_dispersion_equation(self, w, c):
        """ The dispersion equation for Love Waves for value for given frequency and phase velocity. """

        assert c < self.beta

        mu = self.beta ** 2 * self.rho
        k = w / c
        s = np.sqrt(k ** 2 - (w / self.beta) ** 2)
        A = self._matrix_for_stack_of_layers_for_love(w, c)

        return -A[1, 0] - mu * s * A[0, 0]

    def _calculate_love_fundamental_mode(self, w):
        """ Calculates the fundamental mode dispersion curve for Love Wave. """

        roots = []

        for w_i in w:
            # start with a value slightly above the minimum velocity in the model
            guess = self.min_beta + 0.1

            # modify the dispersion equation, so that w is fixed and it only depends on c
            dispersion_equation = lambda c: self._love_dispersion_equation(w=w_i, c=c)

            # for values below fundamental mode, dispersion equation is less than 0
            assert dispersion_equation(guess) < 0

            # c has to be less than beta, so only try these values
            while guess < self.beta:

                # if we find a value where the function changed its sign,
                # use scipy.optimize to find a precise root
                if dispersion_equation(guess) > 0:
                    root = optimize.bisect(dispersion_equation, guess - 1, guess)
                    roots.append(root)
                    break
                # otherwise just increase the guess and try again
                else:
                    guess += 1
            # if we did not find the root in the interval, then it does not exist (?)
            else:
                roots.append(np.nan)

        self._love_dispersion_curves.append(roots)

    def __str__(self):
        string = ''

        for i, l in enumerate(reversed(self._layers)):
            string += f'Layer #{i}: alpha={l.alpha} beta={l.beta} rho={l.rho} h={l.h}\n'

        string += f'Half-space: alpha={self.alpha} beta={self.beta} rho={self.rho}'

        return string
