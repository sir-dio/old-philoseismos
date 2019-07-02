""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy.components import TextualFileHeader, BinaryFileHeader
from philoseismos.segy.components import DataMatrix, Geometry
from philoseismos.segy.tools.constants import sample_format_codes as sfc
from philoseismos.segy.tools import ibm
from philoseismos.segy.tools.constants import TH_format_string

import struct


class Segy:
    """ Object that represents a SEG-Y file.

    Fathers all the components: Textual and Binary Headers, DataMatrix, Geometry.

    """

    def __init__(self, file=None):
        """ Creates an empty Segy object.

        If file is specified, loads the contents from that file.

        """

        self.file = file

        self.TFH = TextualFileHeader()
        self.BFH = BinaryFileHeader()
        self.DM = DataMatrix()
        self.G = Geometry()

        if file:
            self.load_file(file)

    # ----- Loading and writing ----- #

    def load_file(self, file):
        """ Loads specified .sgy file into self. """

        self.TFH.load_from_file(file)
        self.BFH.load_from_file(file)
        self.DM.load_from_file(file)
        self.G.load_from_file(file)

    def save_file(self, file, endian='>'):
        """ Saves self into a specified .sgy file. """

        ss, fl, _ = sfc[self.BFH['Sample Format']]
        nt, tl = self.DM.matrix.shape

        self.BFH._update_bytes(endian)
        self.G._apply_coordinates_scalar_before_packing()

        with open(file, 'bw') as f:
            f.write(self.TFH._bytes)
            f.write(self.BFH._bytes)

            if not fl:  # IBM
                for i in range(nt):
                    raw_header = bytearray(240)
                    raw_header[:232] = struct.pack(endian + TH_format_string, *self.G.table.loc[i, :].values)
                    f.write(raw_header)

                    raw_trace = ibm.pack_ibm32_series(endian, self.DM.matrix[i])
                    f.write(raw_trace)
            else:
                format_string = endian + fl * tl
                for i in range(nt):
                    raw_header = bytearray(240)
                    raw_header[:232] = struct.pack(endian + TH_format_string, *self.G.table.loc[i, :].values)
                    f.write(raw_header)

                    raw_trace = struct.pack(format_string, *self.DM.matrix[i])
                    f.write(raw_trace)

        self.G._apply_coordinate_scalar_after_unpacking()
