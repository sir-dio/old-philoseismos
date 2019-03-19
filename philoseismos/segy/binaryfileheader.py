""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import pandas as pd
import struct

from philoseismos.segy.tools.constants import BFH_columns
from philoseismos.segy.tools.constants import bfh_string


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
        self._table = pd.Series(index=BFH_columns, dtype='int64')
        self._table.fillna(0, inplace=True)

    def check_mandatory_fields(self):
        return True

    def autofill(self):
        """ """

        self._table.fillna(value=0, inplace=True)

    def print_filled(self):
        pass

    # ========================== #
    # ===== Dunder methods ===== #

    def __repr__(self):
        return str(self._table.loc[self._table != 0])

    def __str__(self):
        return str(self._table)

    def __getitem__(self, key):
        return self._table[key]

    # ============================ #
    # ===== Internal methods ===== #

    def _unpack_from_byteSegy(self):
        """ """

        bytearray_ = self._segy._byteSegy.bfh

        # construct the full format string using the endian:
        fs = self._segy.endian + bfh_string

        # unpack the BFH bytes using the format string:
        unpacked = struct.unpack(fs, bytearray_)

        # construct new table:
        updated_table = pd.Series(index=BFH_columns, data=unpacked)

        # check for forced sample format for the Segy:
        if self._segy.fsf:

            updated_table['Sample Format'] = self._segy.fsf

        # update the table:
        self._table.update(updated_table)

    def _pack_to_byteSegy(self):
        """ """

        # construct the full format string using the endian:
        fs = self._segy.endian + bfh_string

        # pack the BFH bytes using the format string:
        packed = struct.pack(fs, *self._table.values)

        # put the packed values into the byteSegy:
        self._segy._byteSegy.bfh = packed

    # ============================ #
    # ===== Updating methods ===== #

    def _update_from_dictionary(self, dictionary):
        """ """

        # a method that does that in pandas is update():

        self._table.update(pd.Series(dictionary))
