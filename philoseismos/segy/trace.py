""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import numpy as np
import struct

from philoseismos.segy.traceheader import TraceHeader
from philoseismos.segy.tools import ibm


class Trace:

    """ """

    def __init__(self, data, id_):
        """ """

        # store a reference to the Data object:
        self._data = data

        # keep the id:
        self.id = id_

        # initialize a Trace Header object:
        self.Header = TraceHeader(trace=self)

    # ========================== #
    # ===== Dunder methods ===== #

    def __repr__(self):
        return f'Trace #{self.id + 1:04}'

    # ============================ #
    # ===== Internal methods ===== #

    def _unpack_from_byteSegy(self):
        """ """

        # separate the value bytes and trace header bytes:
        bytearray_ = self._get_bytes_from_byteSegy()
        header_bytes = bytearray_[:240]
        value_bytes = bytearray_[240:]

        # reset and unpack the trace header:
        self.Header = TraceHeader(trace=self)
        self.Header._unpack_from_bytearray(header_bytes)

        # unpack the values:
        endian = self._data._segy.endian

        if self._data._segy.BFH['Sample Format'] == 1:
            ys = ibm.unpack_ibm32_series(bytearray_=value_bytes,
                                         endian=endian)
        else:
            B = self._data.sample_size  # size of one sample
            fs = endian + self._data._format_letter * (len(value_bytes) // B)
            ys = struct.unpack(fs, value_bytes)

        # store the unpacked values in the Data Matrix:
        self._data.DM[self.id] = np.array(ys)
        self.ys = self._data.DM[self.id]

    def _get_values_from_DataMatrix(self):
        """ """

        self.ys = self._data.DM[self.id]

        # reset the trace header:
        self.Header = TraceHeader(trace=self)
        self.Header.set('TRACENO', self.id + 1)
        self.Header.set('COORDSC', 1)
        self.Header.set('ELEVSC', 1)
        self.Header.set('# Samples', self.ys.size)

        sample_inteval = self._data._segy.BFH['Sample Interval']
        self.Header.set('Sample Interval', sample_inteval)
        self.Header.set('Coordinate Units', 1)

    def _pack_to_bytearray(self):
        """ """

        # create an empty bytearray to pack into:
        packed = bytearray()

        # pack the Trace Header:
        packed += self.Header._pack_to_bytearray()

        # pack the values:
        endian = self._data._segy.endian

        if self._data._segy.BFH['Sample Format'] == 1:
            packed += ibm.pack_ibm32_series(values=self.ys,
                                            endian=endian)
        else:
            fs = endian + self._data._format_letter * self.ys.size
            packed += struct.pack(fs, *self.ys)

        return packed

    # =================================== #
    # ===== Internal helper methods ===== #

    def _get_bytes_from_byteSegy(self):
        """ """

        # caclulate start and end positions:
        start = (self._data.trace_size_B + 240) * self.id
        end = (self._data.trace_size_B + 240) * (self.id + 1)

        # return a chunk from the byteSegy.data bytearray:
        return self._data._segy._byteSegy.data[start:end]
