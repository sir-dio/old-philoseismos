""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import pandas as pd
import struct

from philoseismos.segy.tools.constants import BFH_columns


class BinaryFileHeader:

    """ An object representing a SEG-Y Binary File Header.
    Binary File Header consists of 400 bytes of binary values relevant
    to the whole SEG-Y file.
    Certain values in this header are crucial for the processing
    of the data in the file, particularly the sample interval, trace
    length and format code. """

    def __init__(self, segy):
        """ """

        # store a reference to the Segy object:
        self._segy = segy

        # initialize pd.Series to store BFH values:
        self.table = pd.Series(index=BFH_columns, dtype=object)

    def check_mandatory_fields(self):
        return True

    def autofill(self):
        """ """

        self.table.fillna(value=0, inplace=True, downcast=False)
        self.table['# Traces'] = self._segy.Data.num_traces

    def print_filled(self):
        pass

    # ========================== #
    # ===== Dunder methods ===== #

    def __repr__(self):
        return str(self.table)

    # ============================ #
    # ===== Internal methods ===== #

    def _unpack_from_bytearray(self, bytearray_):
        """ """

        # check if the bytearray is of correct size:
        if len(bytearray_) != 400:
            raise ValueError('BFH length does not equal 400')

        # unpack the values into the table:
        self.table['Job ID'] = self._unpack4(1, bytearray_)
        self.table['Line #'] = self._unpack4(5, bytearray_)
        self.table['Sample Interval'] = self._unpack2(17, bytearray_)
        self.table['Samples / Trace'] = self._unpack2(21, bytearray_)

        # check for the forced sample format:
        if self._segy.fsf:
            self.table['Sample Format'] = self._segy.fsf
        else:
            self.table['Sample Format'] = self._unpack2(25, bytearray_)

        # continue unpacking values into the table:
        self.table['# Traces'] = self._unpack8(313, bytearray_)
        self.table['Data Offset'] = self._unpack8(321, bytearray_)
        self.table['# Ext. TFHs'] = self._unpack2(305, bytearray_)

    def _pack_to_bytearray(self):
        """ """

        self.autofill()

        out = bytearray(400)
        out[0:4] = self._pack4(self.table['Job ID'])
        out[4:8] = self._pack4(self.table['Line #'])
        out[16:18] = self._pack2(int(self.table['Sample Interval']))
        out[20:22] = self._pack2(int(self.table['Samples / Trace']))
        out[24:26] = self._pack2(int(self.table['Sample Format']))
        out[312:320] = self._pack8(int(self.table['# Traces']))
        out[320:328] = self._pack8(int(self.table['Data Offset']))
        out[304:306] = self._pack2(int(self.table['# Ext. TFHs']))

        return out

    # ============================ #
    # ===== Updating methods ===== #

    def _update_from_dictionary(self, dictionary):
        """ """

        # a method that does that in pandas is update():
        self.table.update(pd.Series(dictionary))

    # =================================== #
    # ===== Internal helper methods ===== #

    def _unpack2(self, fb, bytearray_):
        """ """
        fs = self._segy.endian + 'h'
        return struct.unpack(fs, bytearray_[fb - 1:fb + 1])[0]

    def _unpack4(self, fb, bytearray_):
        """ """
        fs = self._segy.endian + 'i'
        return struct.unpack(fs, bytearray_[fb - 1:fb + 3])[0]

    def _unpack8(self, fb, bytearray_):
        """ """
        fs = self._segy.endian + 'Q'
        return struct.unpack(fs, bytearray_[fb - 1:fb + 7])[0]

    def _pack2(self, value):
        """ """
        fs = self._segy.endian + 'h'
        return struct.pack(fs, value)

    def _pack4(self, value):
        """ """
        fs = self._segy.endian + 'i'
        return struct.pack(fs, value)

    def _pack8(self, value):
        """ """
        fs = self._segy.endian + 'Q'
        return struct.pack(fs, value)
