""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy.tools.constants import BFH_columns, BFH_format_string
from philoseismos.segy import gfunc

import pandas as pd
import numpy as np

import struct


class BinaryFileHeader:
    """ Binary File Header for the SEG-Y file.

    Binary File Header consists of 400 bytes of binary values relevant
    to the whole SEG-Y file.
    Certain values in this header are crucial for the processing
    of the data in the file, particularly the sample interval, trace
    length and sample format code.

     """

    def __init__(self):
        """ Create an empty Binary File Header object. """

        self._bytes = None

        self.table = pd.Series(index=BFH_columns, dtype=np.int64)
        self.table.fillna(0, inplace=True)

    # ----- Loading, writing ----- #

    def load_from_file(self, file):
        """ Loads the bytes representing a Binary File Header. """

        endian = gfunc.get_endianness(file)
        full_format_string = endian + BFH_format_string

        with open(file, 'br') as f:
            f.seek(3200)
            self._bytes = f.read(400)

        unpacked = struct.unpack(full_format_string, self._bytes)
        table = pd.Series(index=BFH_columns, data=unpacked)
        self.table.update(table)

    # ----- Working with files ----- #

    def replace_in_file(self, file):
        """ Replaces the Binary File Header in the file with self. """

        endian = gfunc.get_endianness(file)

        full_format_string = endian + BFH_format_string
        self._bytes = struct.pack(full_format_string, *self.table.values)

        with open(file, 'br') as f:
            file_content = bytearray(f.read())

        file_content[3200:3600] = self._bytes

        with open(file, 'bw') as f:
            f.write(file_content)

        # --- Text files --- #

    def export_to_csv(self, file):
        """ Saves the content of the Binary File Header in .csv format.

        Each line contains a key-value pair separated by a comma. """

        self.table.to_csv(file)

    def import_from_csv(self, file):
        """ Loads the content from the .txt file.

        File should have each key-value pair on separate lines,
        separated by a colon. Missing or incorrectly specified keys
        will be assigned the value of 0.

        """

        self.table = pd.Series(index=BFH_columns, dtype=np.int64)
        self.table.fillna(0, inplace=True)

        imported = pd.read_csv(file, squeeze=True, index_col=0, header=None,
                               skipinitialspace=True, names=['Field', 'BFH'])

        self.table.update(imported)

    # ----- Dunder methods ----- #

    def __repr__(self):
        return str(self.table.loc[self.table != 0])

    def __str__(self):
        return str(self.table)

    def __getitem__(self, key):
        return self.table[key]

    def __setitem__(self, key, value):
        self.table[key] = value
