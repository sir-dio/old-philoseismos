""" philoseismos: with passion for the seismic method.

This file defines a DataMatrix object that stores the traces in form
of a numpy 2D array.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy import gfunc
from philoseismos.segy.tools.constants import sample_format_codes as sfc
from philoseismos.segy.tools import ibm
from philoseismos.segy.tools.constants import data_type_map1, unpack_pbar_params

import numpy as np
import struct
import os.path

from tqdm import tqdm


class DataMatrix:
    """ This object represents traces in form of a matrix.

     Each row corresponds to one trace, each column - to one
     sample in a trace.

     """

    def __init__(self, file=None, progress=False):
        """ """

        self.matrix = None
        self.normalization_mode = 'individual'  # can also be "whole"

        if file:
            self.load_from_file(file, progress=progress)

    # ----- Normalized ----- #
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
        endian, fl, tl, ss, nt, dtype = self._get_parameters_from_file(file)

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

    def replace_in_file(self, file):
        """ Replaces the traces in the file with self.

        Parameters
        ----------
        file : str
            Path to the SEG-Y file to replace Data Matrix in.
        """

        endian, fl, tl, ss, nt, dtype = self._get_parameters_from_file(file)

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
            f.seek(3220)
            tl_bytes = f.read(2)
            f.seek(3224)
            sf_bytes = f.read(2)
            f.seek(3512)
            nt_bytes = f.read(8)

        endian = gfunc._detect_endianness_from_sample_format_bytes(sf_bytes)

        tl = struct.unpack(endian + 'h', tl_bytes)[0]
        sf = struct.unpack(endian + 'h', sf_bytes)[0]
        nt = struct.unpack(endian + 'Q', nt_bytes)[0]

        sample_size, format_letter, _ = sfc[sf]
        dtype = data_type_map1[sf]

        if nt == 0:
            data_size = os.path.getsize(file) - 3600
            nt = int(data_size / (sample_size * tl + 240))

        return endian, format_letter, tl, sample_size, nt, dtype
