""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import struct
import pandas as pd

from philoseismos.segy.tools.constants import trace_header_columns
from philoseismos.segy.tools.constants import trace_header_str


class TraceHeader:

    """ An object, representing a Standart Trace Header.
        The values included in the Trace Headers
        are limited and intended to provide information that
        may change on a trace-by-trace basis and the basic
        information needed to process and identify the trace."""

    def __init__(self, trace):
        """ """

        # store a reference to the Trace object:
        self._trace = trace

        # store a reference to the big geometry table:
        self._table = self._trace._data.geometry.iloc[self._trace.id]

        # initialize and empty name:
        self.TH_name = f'SEG{trace.id:05}'

    def set(self, field, value):
        """ """

        self._table[field] = value

    # ========================== #
    # ===== Dunder methods ===== #

    def __repr__(self):
        return str(self._table)

    def __getitem__(self, key):
        return self._table[key]

    # ============================ #
    # ===== Internal methods ===== #

    def _unpack_from_bytearray(self, bytearray_):
        """ """

        # check if the bytearray is of correct size:
        if len(bytearray_) != 240:
            raise ValueError('Trace Header length does not equal 240')

        # construct the full format string using the endian
        fs = self._trace._data._segy.endian + trace_header_str

        # unpack the Trace Header bytes using the format string:
        unpacked = list(struct.unpack(fs, bytearray_[:232]))

        # apply the coordinate scalar, stored in COORDSC header (index 20):
        if unpacked[20] < 0:  # if negative, to be used as a divisor
            div = abs(unpacked[20])
            unpacked[21] /= div  # SOU_X
            unpacked[22] /= div  # SOU_Y
            unpacked[23] /= div  # REC_X
            unpacked[24] /= div  # REC_Y
            unpacked[71] /= div  # CDP_X
            unpacked[72] /= div  # CDP_Y
        else:   # if positive, to be used as a multiplier
            if unpacked[20] == 0:  # 0 should be treated as 1
                unpacked[20] = 1
            mul = unpacked[20]
            unpacked[21] *= mul  # SOU_X
            unpacked[22] *= mul  # SOU_Y
            unpacked[23] *= mul  # REC_X
            unpacked[24] *= mul  # REC_Y
            unpacked[71] *= mul  # CDP_X
            unpacked[72] *= mul  # CDP_Y

        # and then unpack last 8 bytes:
        self.TH_name = bytearray_[232:].decode('cp500')

        # update the table:
        self._trace._data.geometry.iloc[self._trace.id][:] = unpacked

    def _pack_to_bytearray(self):
        """ """

        # grab the values from self._table:
        values = self._table.values

        # apply the coordinate scalar:
        if self['COORDSC'] < 0:
            mul = abs(self['COORDSC'])
            values[21] = int(values[21] * mul)  # SOU_X
            values[22] = int(values[22] * mul)  # SOU_Y
            values[23] = int(values[23] * mul)  # REC_X
            values[24] = int(values[24] * mul)  # REC_Y
            values[71] = int(values[71] * mul)  # CDP_X
            values[72] = int(values[72] * mul)  # CDP_Y
        else:
            div = self['COORDSC']
            values[21] = int(values[21] / div)  # SOU_X
            values[22] = int(values[22] / div)  # SOU_Y
            values[23] = int(values[23] / div)  # REC_X
            values[24] = int(values[24] / div)  # REC_Y
            values[71] = int(values[71] / div)  # CDP_X
            values[72] = int(values[72] / div)  # CDP_Y

        # construct the full format string using the endian
        fs = self._trace._data._segy.endian + trace_header_str

        # pack the values:
        packed = struct.pack(fs, *values)

        # and then pack the last 8 bytes:
        packed += self.TH_name.encode('cp500')

        return packed

    # =================================== #
    # ===== Internal helper methods ===== #
