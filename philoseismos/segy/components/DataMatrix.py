""" philoseismos: with passion for the seismic method.

This file defines a DataMatrix object that stores the traces in form
of a numpy 2D array.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import os.path
import struct

import numpy as np
import scipy.fftpack as fft
from tqdm import tqdm

from philoseismos.segy import gfunc
from philoseismos.segy.tools import ibm
from philoseismos.segy.tools.constants import data_type_map1, unpack_pbar_params
from philoseismos.segy.tools.constants import sample_format_codes as sfc


class DataMatrix:
    """ This object represents traces in form of a matrix.

     Each row corresponds to one trace, each column - to one
     sample in a trace.

     """

    def __init__(self, file=None, progress=False):
        """ Create a new Data Matrix. """

        self.matrix = None

        self.t = None
        self.dt = None

        self._parent = None

        if file:
            self.load_from_file(file, progress=progress)

    def crop_traces(self, end_time):
        """ Set new length for traces.

        Args:
            end_time : End time in ms.

        """

        self.matrix = self.matrix[:, self.t < end_time]
        self.t = self.t[self.t < end_time]

    def average_spectrum(self):
        """ Compute the average amplitude spectrum of the traces.

        Returns:
            freq : The frequency axis.
            amps : The average amplitude spectrum.

        """

        spectrum = np.abs(fft.fft(self.matrix))
        avg_spectrum = np.average(spectrum, axis=0)
        freq = fft.fftfreq(avg_spectrum.size, d=self.dt / 1e3)

        # only return a half of the spectrum (0 Hz to Nyquist frequency)
        avg_spectrum = avg_spectrum[freq > 0]
        freq = freq[freq > 0]

        return freq, avg_spectrum

    def dispersion_image(self, c_max, c_min=1, c_step=1, f_max=150):
        """ Compute the dispersion image for the traces.

        Make sure that the OFFSET header in the Geometry is filled correctly!

        Args:
            c_max: Maximum phase velocity to include.
            c_min: Minimum phase velocity to include.
            c_step: Step for the phase velocities.
            f_max: Maximum frequency to consider. Defaults to 150 Hz.

        Returns:
            V: A 2D array (phase velocity, frequency) that contains values for the dispersion image.

        Notes:
            The algorithm used to calculate the dispersion image is described in Park et al. - 1998 -
            Imaging dispersion curves of surface waves on multi-channel record.

            Extent of the returned image will be [0, f_max, 1, c_max]

        """

        # first we calculate U(x, w)
        U = fft.fft(self.matrix)
        f = fft.fftfreq(n=U.shape[1], d=self.dt / 1e3)

        # leave only the needed frequencies
        U, f = U[:, f >= 0], f[f >= 0]
        U, f = U[:, f <= f_max], f[f <= f_max]

        # extract the phase spectrum
        P = np.angle(U)

        # convert frequency to angular frequency
        ws = 2 * np.pi * f

        # construct an array of phase velocities to try
        cs = np.arange(c_min, c_max + c_step, c_step)

        # get the offset array from the Geometry table
        xs = self._parent.G.OFFSET.values

        # create an array to store V
        V = np.empty(shape=(cs.size, f.size), dtype=complex)

        # iterate over frequencies and velocities
        for i, w in enumerate(ws):
            for j, c in enumerate(cs):
                _v = np.exp(1j * (w * xs / c + P[:, i]))
                V[cs.size - 1 - j, i] = _v.sum()

        return V

    # ----- Properties ----- #

    @property
    def normalized(self):
        """ Returns a normalized version of self.matrix.

        Normalization is individual, meaning that each trace is divided by
        its own maximum value.

        """

        factor = self.matrix.max(axis=1)
        factor[factor == 0] = 1
        return self.matrix / factor[:, np.newaxis]

    # ----- Loading, writing ----- #

    def load_from_file(self, file, progress=False):
        """ Returns a DataMatrix object extracted from the file.

        Args:
            file: A path to the file.
            progress: Toggle the progress bar (disabled by default).

        """

        # endian, format letter, trace length, sample size, number of traces, numpy data type
        endian, fl, tl, ss, nt, dtype, si = self._get_parameters_from_file(file)

        self.matrix = np.empty(shape=(nt, tl), dtype=dtype)

        with open(file, 'br') as f:
            f.seek(3600)  # skip Textual and Binary file headers

            if not fl:  # for IBM values format letter is None
                if progress:
                    with tqdm(total=nt, **unpack_pbar_params) as pbar:
                        for i in range(nt):
                            f.seek(f.tell() + 240)  # skip trace header
                            raw_trace = f.read(ss * tl)  # the size of the trace is (trace length) * (sample size)

                            values = ibm.unpack_ibm32_series(endian, bytearray(raw_trace))
                            self.matrix[i] = values
                            pbar.update(1)
                else:
                    for i in range(nt):
                        f.seek(f.tell() + 240)  # skip trace header
                        raw_trace = f.read(ss * tl)  # the size of the trace is (trace length) * (sample size)

                        values = ibm.unpack_ibm32_series(endian, bytearray(raw_trace))
                        self.matrix[i] = values

            else:
                format_string = endian + fl * tl

                if progress:
                    with tqdm(total=nt, **unpack_pbar_params) as pbar:
                        for i in range(nt):
                            f.seek(f.tell() + 240)  # skip trace header
                            raw_trace = f.read(ss * tl)  # the size of the trace is (trace length) * (sample size)

                            values = struct.unpack(format_string, raw_trace)
                            self.matrix[i] = values
                            pbar.update(1)
                else:
                    for i in range(nt):
                        f.seek(f.tell() + 240)  # skip trace header
                        raw_trace = f.read(ss * tl)  # the size of the trace is (trace length) * (sample size)

                        values = struct.unpack(format_string, raw_trace)
                        self.matrix[i] = values

        # generate time axis
        self.dt = si / 1e3  # convert to ms
        self.t = np.arange(0, tl * self.dt, self.dt)

    def replace_in_file(self, file):
        """ Replaces the traces in the file with self.

        Parameters
        ----------
        file : str
            Path to the SEG-Y file to replace Data Matrix in.
        """

        endian, fl, tl, ss, nt, dtype, si = self._get_parameters_from_file(file)

        if self.matrix.shape != (nt, tl):
            raise ValueError('Matrix shape does not fit the file!')

        if self.matrix.dtype != dtype:
            raise ValueError('Matrix data type does not match the file!')

        with open(file, 'br+') as f:
            f.seek(3600)

            if not fl:
                for i in range(nt):
                    f.seek(f.tell() + 240)
                    raw_trace = ibm.pack_ibm32_series(endian, self.matrix[i])
                    f.write(raw_trace)
            else:
                format_string = endian + fl * tl
                for i in range(nt):
                    f.seek(f.tell() + 240)
                    raw_trace = struct.pack(format_string, *self.matrix[i])
                    f.write(raw_trace)

    # ----- Dunder methods ----- #

    def __repr__(self):
        return str(self.matrix)

    # ----- Static methods ----- #

    @staticmethod
    def _get_parameters_from_file(file):
        """ Returns all the parameters needed to load the traces.

        All these values can be extracted one by one using functions
        defined in philoseismos.segy.gfunc, this method is an alternative
        which only opens the file once, not once per value.

        Parameters
        ----------
        file : str
            Path to the SEG-Y file to extract parameters from.

        Returns
        -------
        endian : str
            Either '>' or '<', for big and little endian respectively.
        format_letter : str
           Format letter used in struct module to pack and unpack binary data.
        tl : int
            Trace length in samples.
        sample_size : int
            Size of one sample in bytes.
        nt : int
            Number of traces in the file.
        dtype : type
            Data type to create a matrix with.

        """

        with open(file, 'br') as f:
            f.seek(3216)
            si_bytes = f.read(2)
            f.seek(3220)
            tl_bytes = f.read(2)
            f.seek(3224)
            sf_bytes = f.read(2)
            f.seek(3512)
            nt_bytes = f.read(8)

        endian = gfunc._detect_endianness_from_sample_format_bytes(sf_bytes)

        si = struct.unpack(endian + 'h', si_bytes)[0]
        tl = struct.unpack(endian + 'h', tl_bytes)[0]
        sf = struct.unpack(endian + 'h', sf_bytes)[0]
        nt = struct.unpack(endian + 'Q', nt_bytes)[0]

        sample_size, format_letter, _ = sfc[sf]
        dtype = data_type_map1[sf]

        if nt == 0:
            data_size = os.path.getsize(file) - 3600
            nt = int(data_size / (sample_size * tl + 240))

        return endian, format_letter, tl, sample_size, nt, dtype, si
