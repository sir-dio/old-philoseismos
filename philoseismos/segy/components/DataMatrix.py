""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy import gfunc
from philoseismos.segy.tools.constants import sample_format_codes as sfc
from philoseismos.segy.tools import ibm

import numpy as np
import struct
import os.path


class DataMatrix:
    """ This object represents traces in form of a matrix.

     Each row corresponds to one trace, each column - to one
     sample in a trace.

     """

    def __init__(self):
        """ """

        self.matrix = None

    # ----- Loading, writing ----- #

    def load_from_file(self, file):
        """ Returns a Data Matrix object extracted from the file. """

        # endian, format letter, trace length, sample size, number of traces
        endian, fl, tl, ss, nt = self._get_parameters_from_file(file)

        self.matrix = np.empty(shape=(nt, tl))

        with open(file, 'br') as f:
            f.seek(3600)  # skip Textual and Binary file headers

            if not fl:  # for IBM values format letter is None
                for i in range(nt):
                    f.seek(f.tell() + 240)  # skip trace header
                    raw_trace = f.read(ss * tl)  # the size of the trace is (trace length) * (sample size)

                    values = ibm.unpack_ibm32_series(endian, raw_trace)
                    self.matrix[i] = values
            else:
                format_string = endian + fl * tl
                for i in range(nt):
                    f.seek(f.tell() + 240)  # skip trace header
                    raw_trace = f.read(ss * tl)  # the size of the trace is (trace length) * (sample size)

                    values = struct.unpack(format_string, raw_trace)
                    self.matrix[i] = values

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

        Returns a tuple:
        (endian, format letter for struct, trace length in samples,
        sample size, number of traces).

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

        if nt == 0:
            data_size = os.path.getsize(file) - 3600
            nt = int(data_size / (sample_size * tl + 240))

        return endian, format_letter, tl, sample_size, nt
