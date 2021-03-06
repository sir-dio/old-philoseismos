""" philoseismos: with passion for the seismic method.

This files defines the Horizontally Layered Model class.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import numpy as np
from scipy import optimize

from philoseismos.models.layer import Layer
from philoseismos import Segy


# TODO: existence of Love waves condition check

class HorizontallyLayeredModel:

    def __init__(self, alpha, beta, rho, Q=0):
        """ Create a new HLM: represented by the half-space.

        To add layers on top of the half-space, use add_layer() method.

        Args:
            alpha (float): P-wave velocity in m / s.
            beta (float): S-wave velocity in m / s.
            rho (float): Density in kg / m^3.

        """

        if alpha and beta >= alpha:
            raise ValueError('Shear wave velocity definitely should be lower than compressional wave velocity!')

        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.Q = Q

        self.fs = None
        self.omegas = None

        # container for all the Layer objects
        self._layers = []

        # containers for modal dispersion curves for Love and Rayleigh waves
        self._love_dispersion_curves = []
        self._rayleigh_dispersion_curves = []

    def add_layer(self, alpha, beta, rho, h, Q=0):
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

        layer = Layer(alpha=alpha, beta=beta, rho=rho, h=h, Q=Q)
        self._layers.append(layer)

    def set_frequency_axis(self, fs):
        """ Set the frequency axis for dispersion curves. """

        self.fs = fs
        self.omegas = fs * 2 * np.pi

    def calculate_love_dispersion_curves(self, n: int):
        """ Calculate n first modal dispersion curves for Love waves.

        Start with the fundamental mode, end with (n-1)th higher mode.

        """

        # TODO: implement reverse matrix algorithm which should be more stable at higher frequencies.

        if self.omegas is None:
            raise ValueError('First assign the frequency axis!')

        if n <= 0:
            return

        self._love_dispersion_curves = []

        self._calculate_love_fundamental_mode()
        for i in range(n - 1):
            self._calculate_love_next_higher_mode()

    def calculate_rayleigh_dispersion_curves(self, n: int):
        """ Calculate n first modal dispersion curves for Rayleigh waves. """

        if self.omegas is None:
            raise ValueError('First assign the frequency axis!')

        if n <= 0:
            return

        self._rayleigh_dispersion_curves = []

        self._calculate_rayleigh_fundamental_mode()
        for i in range(n - 1):
            self._calculate_rayleigh_next_higher_mode()

    def parameter_profiles(self, half_space_h=5):
        """ Return the depths and corresponding parameters of the layers to plot.

        Args:
            half_space_h: How deep should the layer representing the half-space be in m.

        Returns:
            depths, alphas, betas, rhos: Lists of parameters.

        """

        current_depth = 0
        depths, alphas, betas, rhos, qs = [], [], [], [], []

        # for all the layers top to bottom
        for layer in reversed(self._layers):
            depths += [current_depth, current_depth + layer.h]
            alphas += [layer.alpha] * 2
            betas += [layer.beta] * 2
            rhos += [layer.rho] * 2
            qs += [layer.Q] * 2

            current_depth += layer.h

        # for the half-space
        depths += [current_depth, current_depth + half_space_h]
        alphas += [self.alpha] * 2
        betas += [self.beta] * 2
        rhos += [self.rho] * 2
        qs += [self.Q] * 2

        return depths, alphas, betas, rhos, qs

    def parameter_profiles_for_z(self, z0, z1, dz):
        """ Return the parameters of the layers corresponding to a given depth curve.

        Args:
            z0 : Start of the depth interval.
            z1 : End of the depth interval (included).
            dz : Step for the depth interval.

        Returns:
            depths, alphas, betas, rhos: Lists of parameters.

        """

        # TODO: support slicing of the model

        depths = np.arange(z0, z1 + dz, dz)

        alphas = np.empty_like(depths)
        betas = np.empty_like(depths)
        rhos = np.empty_like(depths)
        qs = np.empty_like(depths)

        index = 0

        for layer in self.layers[::-1]:
            alpha, beta, rho, q = layer.parameter_lines(dz=dz)

            alphas[index:index + alpha.size] = alpha
            betas[index:index + alpha.size] = beta
            rhos[index:index + alpha.size] = rho
            qs[index:index + alpha.size] = q

            index += alpha.size

        alphas[index:] = self.alpha
        betas[index:] = self.beta
        rhos[index:] = self.rho
        qs[index:] = self.Q

        return depths, alphas, betas, rhos, qs

    def export_to_sgy_for_tesseral(self, x0, x1, dx, z0, z1, dz, base_filename):
        """ Export model to SEG-Y format for use in Tesseral.

        Args:
            x0 : Start of the x axis.
            x1 : End of the x axis.
            dx : Step for x axis.
            z0 : Start of the z axis.
            z1 : End of the z axis.
            dz : Step for the z axis.
            base_filename : Base file name for resulitng SEG-Y files. The parameter name and
                file extension will be appended automatically.

        Notes:
            Creates three SEG-Y files: one with values of Vp, one with values of Vs, and one
            with values of rho.

        """

        x_coord = np.arange(x0, x1 + dx, dx)
        z_coord, alphas, betas, rhos, qs = self.parameter_profiles_for_z(z0=z0, z1=z1, dz=dz)

        alpha_sgy = Segy.empty(shape=(x_coord.size, z_coord.size), sample_interval=dz * 1000)
        beta_sgy = Segy.empty(shape=(x_coord.size, z_coord.size), sample_interval=dz * 1000)
        rho_sgy = Segy.empty(shape=(x_coord.size, z_coord.size), sample_interval=dz * 1000)
        q_sgy = Segy.empty(shape=(x_coord.size, z_coord.size), sample_interval=dz * 1000)

        alpha_sgy.G.table.loc[:, 'COORDSC'] = -1000
        alpha_sgy.G.table.loc[:, 'ELEVSC'] = -1000
        alpha_sgy.G.table.loc[:, 'REC_X'] = x_coord

        beta_sgy.G.table.loc[:, 'COORDSC'] = -1000
        beta_sgy.G.table.loc[:, 'ELEVSC'] = -1000
        beta_sgy.G.table.loc[:, 'REC_X'] = x_coord

        rho_sgy.G.table.loc[:, 'COORDSC'] = -1000
        rho_sgy.G.table.loc[:, 'ELEVSC'] = -1000
        rho_sgy.G.table.loc[:, 'REC_X'] = x_coord

        q_sgy.G.table.loc[:, 'COORDSC'] = -1000
        q_sgy.G.table.loc[:, 'ELEVSC'] = -1000
        q_sgy.G.table.loc[:, 'REC_X'] = x_coord

        alpha_sgy.DM.matrix[:] = alphas
        beta_sgy.DM.matrix[:] = betas
        rho_sgy.DM.matrix[:] = rhos
        q_sgy.DM.matrix[:] = qs

        alpha_sgy.save_file(base_filename + '_Vp.sgy')
        beta_sgy.save_file(base_filename + '_Vs.sgy')
        rho_sgy.save_file(base_filename + '_Rho.sgy')
        q_sgy.save_file(base_filename + '_Q.sgy')

    @property
    def layers(self):
        return tuple(self._layers)

    @property
    def min_beta(self):
        betas = [layer.beta for layer in self._layers]
        betas.append(self.beta)
        return min(betas)

    @property
    def max_beta(self):
        betas = [layer.beta for layer in self._layers]
        betas.append(self.beta)
        return max(betas)

    @property
    def love_dispersion_curves(self):
        return tuple(self._love_dispersion_curves)

    @property
    def rayleigh_dispersion_curves(self):
        return tuple(self._rayleigh_dispersion_curves)

    @property
    def cumulative_layer_h(self):
        return sum([l.h for l in self.layers])

    def _matrix_for_stack_of_layers_for_love(self, w, c):
        """ Calculate the matrix for stack of layers for Love waves. """

        A = np.identity(2)

        for layer in self._layers:
            A = np.matmul(A, layer.layer_matrix_love(w, c))

        return A

    def _matrix_for_stack_of_layers_for_rayleigh(self, w, c):
        """ Calculate the matrix for stack of layers for Rayleigh waves. """

        A = np.identity(4)

        for layer in self._layers:
            A = np.matmul(A, layer.layer_matrix_rayleigh(w, c))

        return A

    def _love_dispersion_function(self, w, c):
        """ The dispersion function for Love Waves. """

        assert c < self.beta, f'beta: {self.beta}, c: {c}'

        mu = self.beta ** 2 * self.rho
        k = w / c
        s = np.sqrt(k ** 2 - (w / self.beta) ** 2)
        A = self._matrix_for_stack_of_layers_for_love(w, c)

        return -A[1, 0] - mu * s * A[0, 0]

    def _rayleigh_dispersion_function(self, w, c):
        """ The dispersion function for Rayleigh Waves. """

        A = self._matrix_for_stack_of_layers_for_rayleigh(w, c)

        # normalize the matrix to avoid overflow issues (hopefully)
        A = A / A.max() * 2

        r = np.lib.scimath.sqrt(1 - (c / self.alpha) ** 2)
        s = np.lib.scimath.sqrt(1 - (c / self.beta) ** 2)

        gamma = 2 * (self.beta / c) ** 2
        delta = gamma - 1

        L1 = A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]
        L2 = A[0, 0] * A[2, 1] - A[0, 1] * A[2, 0]
        L3 = A[0, 0] * A[3, 1] - A[0, 1] * A[3, 0]
        L4 = A[1, 0] * A[2, 1] - A[1, 1] * A[2, 0]
        L5 = A[1, 0] * A[3, 1] - A[1, 1] * A[3, 0]
        L6 = A[2, 0] * A[3, 1] - A[2, 1] * A[3, 0]

        H1 = self.rho * (gamma ** 2 * r * s - delta ** 2)
        H2 = -self.rho * r
        H3 = H4 = self.rho * (gamma * r * s - delta)
        H5 = -self.rho * s
        H6 = 1 - r * s

        return L1 * H1 + L2 * H2 + L3 * H3 + L4 * H4 + L5 * H5 + L6 * H6

    def _calculate_love_fundamental_mode(self):
        """ Calculates the fundamental mode dispersion curve for Love waves. """

        # a list with the values of the phase velocity that satisfy the
        # dispersion equation
        roots = []

        # for each given value of circular frequency, find the value of
        # phase velocity that satisfies the dispersion equation
        for w in self.omegas:
            # start with a value slightly above the minimum velocity in the model
            # NB! for high frequencies, this step can cause initial guesses to fall
            # above fundamental mode. the function will raise AssertionError in this case.
            guess = self.min_beta + 0.001

            # modify the dispersion function, so that w is fixed and it only depends on c
            def dispersion_function(c):
                """ Return the left hand side of the dispersion equation for Love waves. """
                return self._love_dispersion_function(w, c)

            # for values below fundamental mode, dispersion equation is less than 0
            assert dispersion_function(guess) <= 0, f'The guess falls above the fundamental mode!'

            # c has to be less than beta, so only try these values
            while guess < self.beta:

                # if we find a value where the function changed its sign,
                # use scipy.optimize to find a precise root
                if dispersion_function(guess) > 0:
                    root = optimize.bisect(dispersion_function, guess - 1, guess)
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
        """ Calculate the next higher mode available for Love waves. """

        if len(self._love_dispersion_curves) < 1:
            raise ValueError('Before calculating the higher modes, calculate the fundamental one.')

        # the algorithm is the same as for the fundamental mode,
        # except the guess is always slightly bigger than the phase
        # velocity of the previous mode

        roots = []

        # iterate over omegas AND the phase velocities of the previous mode
        for w, c_prev in zip(self.omegas, self._love_dispersion_curves[-1]):

            # if c_prev is NaN or next guess will be greater than max beta,
            # go to the next iteration
            if np.isnan(c_prev) or c_prev + 0.1 > self.beta:
                roots.append(np.nan)
                continue

            guess = c_prev + 0.001

            def dispersion_function(c):
                """ Return the left hand side of the dispersion equation for Love waves. """
                return self._love_dispersion_function(w, c)

            # get the sign of the dispersion equation
            sign = np.sign(dispersion_function(guess))

            while guess < self.beta:
                if np.sign(dispersion_function(guess)) != sign:
                    root = optimize.bisect(dispersion_function, guess - 1, guess)
                    roots.append(root)
                    break
                else:
                    guess += 1
            else:
                roots.append(np.nan)

        self._love_dispersion_curves.append(roots)

    def _calculate_rayleigh_fundamental_mode(self):
        """ Calculate the fundamental mode dispersion curve for Rayleigh waves. """

        roots = []

        for w in self.omegas:
            # this guess should probably be based on the Poisson's coefficient
            # but for now I'll just make it 1 because fuck it
            guess = self.min_beta / 2

            def dispersion_function(c):
                """ Return the left hand side of the dispersion equation for Rayleigh waves. """
                return self._rayleigh_dispersion_function(w, c)

            sign = np.sign(dispersion_function(guess))

            # is this condition good? or check for the maximum value of beta?
            while guess < self.max_beta:
                if np.sign(dispersion_function(guess)) != sign:
                    root = optimize.bisect(dispersion_function, guess - 1, guess)
                    roots.append(root)
                    break
                else:
                    guess += 1
            else:
                roots.append(np.nan)

        self._rayleigh_dispersion_curves.append(roots)

    def _calculate_rayleigh_next_higher_mode(self):
        """ Calculate the next higher mode available for Rayleigh waves. """

        if len(self._rayleigh_dispersion_curves) < 1:
            raise ValueError('Before calculating the higher modes, calculate the fundamental one.')

        max_beta = self.max_beta
        roots = []

        for w, c_prev in zip(self.omegas, self._rayleigh_dispersion_curves[-1]):

            # if c_prev equals max_beta, go to the next iteration
            if c_prev == max_beta:
                roots.append(max_beta)
                continue

            guess = c_prev + 0.001

            def dispersion_function(c):
                """ Return the left hand side of the dispersion equation for Love waves. """
                return self._rayleigh_dispersion_function(w, c)

            # get the sign of the dispersion equation
            sign = np.sign(dispersion_function(guess))
            print(sign)

            while guess < max_beta:
                if np.sign(dispersion_function(guess)) != sign:
                    try:
                        root = optimize.bisect(dispersion_function, guess - 1, guess)
                        roots.append(root)
                    # TODO: this hack feel cheaty af.
                    except ValueError:
                        roots.append(max_beta)
                    break
                else:
                    guess += 1
            else:
                roots.append(max_beta)

        self._rayleigh_dispersion_curves.append(roots)

    def __str__(self):
        string = ''

        for i, l in enumerate(reversed(self._layers)):
            string += f'Layer #{i}: alpha={l.alpha} beta={l.beta} rho={l.rho} h={l.h}\n'

        string += f'Half-space: alpha={self.alpha} beta={self.beta} rho={self.rho}'

        return string
