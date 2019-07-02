""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy.components import TextualFileHeader, BinaryFileHeader
from philoseismos.segy.components import DataMatrix, Geometry


class Segy:
    """ Object that represents a SEG-Y file.

    Fathers all the components: Textual and Binary Headers, DataMatrix, Geometry.

    """

    def __init__(self, file):
        """ Creates an empty Segy object. """

        self.TFH = TextualFileHeader()
        self.BFH = BinaryFileHeader()
        self.DM = DataMatrix()
        self.G = Geometry()

        self.load_file(file)

    # ----- Loading and writing ----- #

    def load_file(self, file):
        """ Loads specified .sgy file into self. """

        self.TFH.load_from_file(file)
        self.BFH.load_from_file(file)
        self.DM.load_from_file(file)
        self.G.load_from_file(file)
