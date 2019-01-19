""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import struct


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

    # ========================== #
    # ===== Dunder methods ===== #

    def __repr__(self):
        return str(self.table)

    # ============================ #
    # ===== Internal methods ===== #

    def _unpack_from_bytearray(self, bytearray_):
        """ """

        # check if the bytearray is of correct size:
        if len(bytearray_) != 240:
            raise ValueError('Trace Header length does not equal 240')

        # grab the endian value from the Segy object:
        endian = self._trace._data._segy.endian

        # initiate a table - a link to the big geometry of the Data object
        self.table = self._trace._data.geometry.iloc[self._trace.id]

        self.table['TRACENO'] = self._unpack4(endian, 1, bytearray_)
        self.N = self._trace.id + 1   # trace number within SEG-Y file

        # geometry headers
        self.table['FFID'] = self._unpack4(endian, 9, bytearray_)
        self.table['CHAN'] = self._unpack4(endian, 13, bytearray_)

        self.table['CDP'] = self._unpack4(endian, 21, bytearray_)
        self.table['OFFSET'] = self._unpack4(endian, 37, bytearray_)

        self.table['ELEVSC'] = self._unpack2(endian, 69, bytearray_)
        self.table['COORDSC'] = self._unpack2(endian, 71, bytearray_)

        # Coordinates themselves:
        if self.table['COORDSC'] < 0:  # if negative, to be used as a divisor
            div = abs(self.table['COORDSC'])
            self.table['SOU_X'] = self._unpack4(endian, 73, bytearray_) / div
            self.table['SOU_Y'] = self._unpack4(endian, 77, bytearray_) / div
            self.table['REC_X'] = self._unpack4(endian, 81, bytearray_) / div
            self.table['REC_Y'] = self._unpack4(endian, 85, bytearray_) / div

            self.table['CDP_X'] = self._unpack4(endian, 181, bytearray_) / div
            self.table['CDP_Y'] = self._unpack4(endian, 185, bytearray_) / div
        elif self.table['COORDSC'] == 0:  # zero should be treated as 1
            self.table['COORDSC'] = 1
            self.table['SOU_X'] = self._unpack4(endian, 73, bytearray_)
            self.table['SOU_Y'] = self._unpack4(endian, 77, bytearray_)
            self.table['REC_X'] = self._unpack4(endian, 81, bytearray_)
            self.table['REC_Y'] = self._unpack4(endian, 85, bytearray_)

            self.table['CDP_X'] = self._unpack4(endian, 181, bytearray_)
            self.table['CDP_Y'] = self._unpack4(endian, 185, bytearray_)
        else:  # if positive, to be used as a multiplier
            mul = self.table['COORDSC']
            self.table['SOU_X'] = self._unpack4(endian, 73, bytearray_) * mul
            self.table['SOU_Y'] = self._unpack4(endian, 77, bytearray_) * mul
            self.table['REC_X'] = self._unpack4(endian, 81, bytearray_) * mul
            self.table['REC_Y'] = self._unpack4(endian, 85, bytearray_) * mul

            self.table['CDP_X'] = self._unpack4(endian, 181, bytearray_) * mul
            self.table['CDP_Y'] = self._unpack4(endian, 185, bytearray_) * mul

        # Date and time:
        self.table['YEAR'] = self._unpack2(endian, 157, bytearray_)
        self.table['DAY'] = self._unpack2(endian, 159, bytearray_)
        self.table['HOUR'] = self._unpack2(endian, 161, bytearray_)
        self.table['MINUTE'] = self._unpack2(endian, 163, bytearray_)
        self.table['SECOND'] = self._unpack2(endian, 165, bytearray_)

        self.trace_len = self._unpack2(endian, 115, bytearray_)
        self.table['dt'] = self._unpack2(endian, 117, bytearray_)

        self.coord_units = self._unpack2(endian, 89, bytearray_)
        self.time_basis = self._unpack2(endian, 167, bytearray_)
        self.measurement_unit = self._unpack2(endian, 203, bytearray_)

    def _create_from_dictionary(self, dictionary):
        """ """

        # initiate a table - a link to the big geometry of the Data object
        self.table = self._trace._data.geometry.iloc[self._trace.id]

    # =================================== #
    # ===== Internal helper methods ===== #

    def _unpack2(self, endian, fb, bytearray_):
        """ """
        fs = endian + 'h'
        return struct.unpack(fs, bytearray_[fb - 1:fb + 1])[0]

    def _unpack4(self, endian, fb, bytearray_):
        """ """
        fs = endian + 'i'
        return struct.unpack(fs, bytearray_[fb - 1:fb + 3])[0]
