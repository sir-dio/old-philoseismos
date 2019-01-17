""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import numpy as np
import struct

from philoseismos.segy.traceheader import TraceHeader
from philoseismos.segy.tools import ibm


class Trace:

    """ """

    def __init__(self, data, id):
        """ """

        # store a reference to the Data object:
        self._data = data

        # keep the id:
        self.id = id

        # initialize a Trace Header object:
        self.Header = TraceHeader(trace=self)

    # ========================== #
    # ===== Dunder methods ===== #

    def __repr__(self):
        return f'Trace #{self.id + 1:04}'

    # ============================ #
    # ===== Internal methods ===== #

    def _unpack_from_bytearray(self, bytearray_, sample_format, trace_length):
        """ """

        # separate the value bytes and trace header bytes:
        header_bytes = bytearray_[:240]
        value_bytes = bytearray_[240:]

        # reset and unpack the trace header:
        self.Header = TraceHeader(trace=self)
        self.Header._unpack_from_bytearray(header_bytes)

        # unpack the values:
        endian = self._data._segy.endian

        if sample_format == 1:
            ys = ibm.unpack_ibm32_series(bytearray_=value_bytes,
                                         endian=endian)
        else:
            fcode = endian + self._data._format_letter * trace_length
            ys = struct.unpack(fcode, value_bytes)

        # store the unpacked values in the Data Matrix:
        self._data.DM[self.id] = np.array(ys)
        self.ys = self._data.DM[self.id]

    # =================================== #
    # ===== Internal helper methods ===== #
