""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import struct

from philoseismos.segy.bytesegy import byteSegy
from philoseismos.segy.textualfileheader import TextualFileHeader
from philoseismos.segy.binaryfileheader import BinaryFileHeader
from philoseismos.segy.data import Data
from philoseismos.segy.tools.constants import data_type_map2


class Segy:

    """ Main object for the package. Represents a SEG-Y file and contains
    methods to open, write, modify and create such files.  """

    def __init__(self, file=None, endian='auto', fsf=None, silent=False):
        """ """

        # create a byteSegy instance [to write and read bytes]:
        self._byteSegy = byteSegy(segy=self)

        # keep the parameter values:
        self.file = file
        self.endian = endian
        self.fsf = fsf
        self.silent = silent

        # initialize main objects:
        self.TFH = TextualFileHeader(segy=self)
        self.BFH = BinaryFileHeader(segy=self)
        self.Data = Data(segy=self)

        # if a file is specified, load it:
        if file:
            self.load_file(file=file)
        else:
            self.file = 'None'
            self.endian = '>'

    def load_file(self, file):
        """ """

        self._byteSegy.load_from_file(file=file)

        if self.endian == 'auto':
            self._detect_endiannes()

        self.TFH._unpack_from_byteSegy()
        self.BFH._unpack_from_byteSegy()
        self.Data._unpack_from_byteSegy()

    def save_file(self, file):
        """ """

        self._byteSegy.to_file(file)

    def change_sample_format(self, fsf):
        """ """

        pass

    # ========================== #
    # ===== Dunder methods ===== #

    def __repr__(self):
        return 'Segy(file={})'.format(self.file)

    # ============================ #
    # ===== Internal methods ===== #

    def _detect_endiannes(self):
        """ """

        sample_format_bytes = self._byteSegy.bfh[24:26]
        try:
            assert struct.unpack('>h', sample_format_bytes)[0] < 16
            self.endian = '>'
        except AssertionError:
            self.endian = '<'

    # ============================ #
    # ===== Factory methods ===== #

    @classmethod
    def create_from_DataMatrix(cls, DM, sample_interval=500):
        """ Creates a Segy object from given 2D matrix.

        Parameters
        ----------
        DM : 2D array
            DM stands for Data Matrix. It is a simple numpy 2D array where
            each trace is represented by a row.
        sample_interval : int
            A sample interval in microseconds to use.

        Notes
        -----
        The dtype attribute of the DM is used to choose a sample format for
        the Segy. The endian is set to big by default, but can be changed
        before saving the file if desired. """

        if DM.ndim != 2:
            raise ValueError("The DataMatrix must have exactly 2 dimensions.")

        bfh_values = {'Sample Interval': sample_interval,
                      'Sample Format': data_type_map2[DM.dtype],
                      'Samples / Trace': DM.shape[1],
                      '# Traces': DM.shape[0],
                      'Byte Offset of Data': 3600,
                      'SEG-Y Rev. Major': 2,
                      }

        segy = cls(endian='>')

        segy.BFH._update_from_dictionary(bfh_values)
        segy.Data._import_DataMatrix(DM)

        return segy
