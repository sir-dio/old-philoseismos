""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy.bytesegy import byteSegy
from philoseismos.segy.textualfileheader import TextualFileHeader
from philoseismos.segy.binaryfileheader import BinaryFileHeader
from philoseismos.segy.data import Data
from philoseismos.segy.tools.constants import data_type_map


class Segy:

    """ """

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

        # automatically detect endiannes:
        if self.endian == 'auto':
            try:
                self.endian = '>'

                self._byteSegy.load_from_file(file=file)
                self.TFH._unpack_from_bytearray(self._byteSegy.tfh)
                self.BFH._unpack_from_bytearray(self._byteSegy.bfh)
                params = self.Data._get_unpacking_parameters_from_BFH(self.BFH)
                self.Data._unpack_from_bytearray(self._byteSegy.data, **params)

            # a KeyError is raised when Data objects looks for format
            # strings in the mapping dictionary defined in constants.py
            except KeyError:
                self.endian = '<'

                self._byteSegy.load_from_file(file=file)
                self.TFH._unpack_from_bytearray(self._byteSegy.tfh)
                self.BFH._unpack_from_bytearray(self._byteSegy.bfh)
                params = self.Data._get_unpacking_parameters_from_BFH(self.BFH)
                self.Data._unpack_from_bytearray(self._byteSegy.data, **params)

        # otherwise use specified endiannes:
        else:
            self._byteSegy.load_from_file(file=file)
            self.TFH._unpack_from_bytearray(self._byteSegy.tfh)
            self.BFH._unpack_from_bytearray(self._byteSegy.bfh)
            params = self.Data._get_unpacking_parameters_from_BFH(self.BFH)
            self.Data._unpack_from_bytearray(self._byteSegy.data, **params)

    def change_sample_format(self, fsf):
        pass

    # ============================ #
    # ===== Factory methods ===== #

    @classmethod
    def create_from_DataMatrix(cls, DM, sample_interval=500):
        """ """

        if DM.ndim != 2:
            raise ValueError("The DataMatrix must have exactly 2 dimensions.")

        bfh_values = {'Sample interval': sample_interval,
                      'Sample format': data_type_map[DM.dtype],
                      'Samples / trace': DM.shape[1],
                      '# Traces': DM.shape[0],
                      'Data offset': 3600,
                      }

        segy = cls(endian='>')

        segy.BFH._update_from_dictionary(bfh_values)
        segy.Data._import_DataMatrix(DM)

        return segy
