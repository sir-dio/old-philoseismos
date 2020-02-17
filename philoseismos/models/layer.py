""" philoseismos: with passion for the seismic method.

This files defines the Layer class.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import numpy as np


class Layer:

    def __init__(self, alpha, beta, rho, h):
        """ TODO: decribe """

        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.h = h

    def layer_matrix_love(self, omega, c):
        """ Return a layer matrix for Love Waves for a given phase velocity and frequency. """

        if c == self.beta:
            return np.identity(2)

        k = omega / c
        mu = self.beta ** 2 * self.rho

        s = np.lib.scimath.sqrt((omega / self.beta) ** 2 - k ** 2)
        Q = self.h * s

        a11 = np.cos(Q)
        a12 = np.sin(Q) / mu / s
        a21 = -mu * s * np.sin(Q)
        a22 = a11

        A = np.array([
            [a11, a12],
            [a21, a22]
        ])

        return A

    def layer_matrix_rayleigh(self, omega, c):
        return
