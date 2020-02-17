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

        self.fs = None
        self.omegas = None

        self._layers = []
        self._love_dispersion_curves = []

    def add_layer(self, alpha, beta, rho, h):
        """ Add a layer on top of the HLM. """

        layer = Layer(alpha=alpha, beta=beta, rho=rho, h=h)
        self._layers.append(layer)

    def set_frequency_axis(self, fs):
        """ Set the frequency axis for dispersion curves. """

        self.fs = fs
        self.omegas = fs * 2 * np.pi

    def calculate_love_dispersion_curves(self, n: int):
        """ Calculate n first modal dispersion curves.

        Start with the fundamental mode, end with (n-1)th higher mode.

        """

        if self.omegas is None:
            raise ValueError('First assign the frequency axis!')

        if n <= 0:
            return

        self._calculate_love_fundamental_mode()
        for i in range(n - 1):
            self._calculate_love_next_higher_mode()

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

    def _calculate_love_fundamental_mode(self):
        """ Calculates the fundamental mode dispersion curve for Love Wave. """

        # a list with the values of the phase velocity that satisfy the
        # dispersion equation
        roots = []

        # for each given value of circular frequency, find the value of
        # phase velocity that satisfies the dispersion equation
        for w in self.omegas:
            # start with a value slightly above the minimum velocity in the model
            guess = self.min_beta + 0.1

            # modify the dispersion equation, so that w is fixed and it only depends on c
            def dispersion_equation(c):
                """ Return the left hand side of the dispersion equation for Love waves. """
                return self._love_dispersion_equation(w, c)

            # for values below fundamental mode, dispersion equation is less than 0
            assert dispersion_equation(guess) <= 0

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
            # if we did not find the root in the interval, move on to the next frequency
            else:
                roots.append(np.nan)

        self._love_dispersion_curves.append(roots)

    def _calculate_love_next_higher_mode(self):
        """ Calculate the next higher mode available. """

        if len(self._love_dispersion_curves) < 1:
            raise ValueError('Before calculating the higher modes, calculate the fundamental one.')

        # the algorithm is the same as for the fundamental mode,
        # except the guess is always slightly bigger than the phase
        # velocity of the previous mode

        roots = []

        # iterate over omegas AND the phase velocities of the previous mode
        for w, c_prev in zip(self.omegas, self._love_dispersion_curves[-1]):

            # if c_prev is NaN, go to the next iteration
            if np.isnan(c_prev):
                roots.append(np.nan)
                continue

            guess = c_prev + 0.1

            def dispersion_equation(c):
                """ Return the left hand side of the dispersion equation for Love waves. """
                return self._love_dispersion_equation(w, c)

            # get the sign of the dispersion equation
            sign = np.sign(dispersion_equation(guess))

            while guess < self.beta:
                if np.sign(dispersion_equation(guess)) != sign:
                    root = optimize.bisect(dispersion_equation, guess - 1, guess)
                    roots.append(root)
                    break
                else:
                    guess += 1
            else:
                roots.append(np.nan)

        self._love_dispersion_curves.append(roots)

    def __str__(self):
        string = ''

        for i, l in enumerate(reversed(self._layers)):
            string += f'Layer #{i}: alpha={l.alpha} beta={l.beta} rho={l.rho} h={l.h}\n'

        string += f'Half-space: alpha={self.alpha} beta={self.beta} rho={self.rho}'

        return string
