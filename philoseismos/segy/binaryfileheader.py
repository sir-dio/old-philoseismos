""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import pandas as pd
import struct

from philoseismos.segy.tools.constants import BFH_columns
from philoseismos.segy.tools.constants import bfh_string1, bfh_string2


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
        self.table = pd.Series(index=BFH_columns, dtype='int64')
        self.table.fillna(0, inplace=True)

    def check_mandatory_fields(self):
        return True

    def autofill(self):
        """ """

        self.table.fillna(value=0, inplace=True)

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

        # construct the full format string using the endian:
        fs1 = self._segy.endian + bfh_string1
        fs2 = self._segy.endian + bfh_string2

        # unpack the BFH bytes using format strings:
        unpacked1 = struct.unpack(fs1, bytearray_[:100])
        unpacked2 = struct.unpack(fs2, bytearray_[300:332])

        # concatenate the results:
        unpacked = unpacked1 + unpacked2

        # construct new table:
        updated_table = pd.Series(index=BFH_columns, data=unpacked)

        # check for forced sample format for the Segy:
        if self._segy.fsf:
            updated_table['Sample Format'] = self._segy.fsf

        # update the table:
        self.table.update(updated_table)

    # ============================ #
    # ===== Updating methods ===== #

    def _update_from_dictionary(self, dictionary):
        """ """

        # a method that does that in pandas is update():
        self.table.update(pd.Series(dictionary))
