""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy import gfunc
from philoseismos.segy.tools.constants import sample_format_codes as sfc
from philoseismos.segy.tools.constants import TH_columns, TH_format_string

import struct
import os
import pandas as pd
import numpy as np


class Geometry:
    """ This object represents geometry: a collection of all the Trace Headers. """

    def __init__(self):
        """ """

        self.table = None
        self.headers = ['TRACENO', 'FFID', 'CHAN',
                        'SOU_X', 'REC_X', 'OFFSET',
                        'CDP_X']

    # ----- Loading, writing ----- #

    def load_from_file(self, file):
        """ Returns a Geometry object extracted from the file. """

        # endian, trace length, sample size, number of traces
        endian, tl, ss, nt = self._get_parameters_from_file(file)

        self.table = pd.DataFrame(index=range(nt), columns=TH_columns)

        with open(file, 'br') as f:
            f.seek(3600)  # skip Textual and Binary file headers
            for i in range(nt):
                raw_header = f.read(240)

                values = struct.unpack(endian + TH_format_string, raw_header[:232])
                self.table.loc[i, :] = values

                f.seek(f.tell() + ss * tl)

        self.table.fillna(0, inplace=True)
        self._apply_coordinate_scalar_after_unpacking()

    def replace_in_file(self, file):
        """ Replaces the geometry in the file with self. """

        endian, tl, ss, nt = self._get_parameters_from_file(file)

        self._apply_coordinates_scalar_before_packing()

        with open(file, 'br+') as f:
            f.seek(3600)
            for i in range(nt):
                raw_header = bytearray(240)
                raw_header[:232] = struct.pack(endian + TH_format_string, *self.table.loc[i, :].values)
                f.write(raw_header)
                f.seek(f.tell() + ss * tl)

        # to restore the table to its true form, we remove the effect of applying scalars
        self._apply_coordinate_scalar_after_unpacking()

        # ----- Dunder methods ----- #

    def __repr__(self):
        return str(self.table.loc[:, self.headers])

    # ----- Static methods ----- #

    @staticmethod
    def _get_parameters_from_file(file):

        """ Returns all the parameters needed to load the geometry.

        All these values can be extracted one by one using functions
        defined in philoseismos.segy.gfunc, this method is an alternative
        which only opens the file once, not once per value.

        Returns a tuple:
        (endian, trace length in samples, sample size, number of traces).

        """

        with open(file, 'br') as f:
            f.seek(3220)
            tl_bytes = f.read(2)
            f.seek(3224)
            sf_bytes = f.read(2)
            f.seek(3512)
            nt_bytes = f.read(8)

        endian = gfunc._detect_endianness_from_sample_format_bytes(sf_bytes)

        tl = struct.unpack(endian + 'h', tl_bytes)[0]
        sf = struct.unpack(endian + 'h', sf_bytes)[0]
        nt = struct.unpack(endian + 'Q', nt_bytes)[0]

        sample_size, _, _ = sfc[sf]

        if nt == 0:
            data_size = os.path.getsize(file) - 3600
            nt = int(data_size / (sample_size * tl + 240))

        return endian, tl, sample_size, nt

    # ----- Internal methods ----- #

    def _apply_coordinate_scalar_after_unpacking(self):
        """ Applies the coordinate scalar to all relevant headers after unpacking. """

        # zero should be treated as one
        self.table['COORDSC'].loc[self.table['COORDSC'] == 0] = 1
        absolute_scalar_value = abs(self.table.COORDSC)

        # if negative, to be used as a divisor
        negative_scalar_indices = self.table.COORDSC < 0

        self.table.loc[negative_scalar_indices, 'SOU_X'] /= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'SOU_Y'] /= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'REC_X'] /= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'REC_Y'] /= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'CDP_X'] /= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'CDP_Y'] /= absolute_scalar_value

        # if positive, to be used as a multiplier
        positive_scalar_indices = self.table.COORDSC > 0

        self.table.loc[positive_scalar_indices, 'SOU_X'] *= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'SOU_Y'] *= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'REC_X'] *= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'REC_Y'] *= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'CDP_X'] *= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'CDP_Y'] *= absolute_scalar_value

    def _apply_coordinates_scalar_before_packing(self):
        """ Applies the coordinate scalar to all relevant headers before packing. """

        # zero should be treated as one
        # self.table['COORDSC'].loc[self.table['COORDSC'] == 0] = 1
        absolute_scalar_value = abs(self.table.COORDSC)

        # when unpacking, if negative, to be used as a divisor,
        # so here we multiply
        negative_scalar_indices = self.table.COORDSC < 0

        self.table.loc[negative_scalar_indices, 'SOU_X'] *= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'SOU_Y'] *= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'REC_X'] *= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'REC_Y'] *= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'CDP_X'] *= absolute_scalar_value
        self.table.loc[negative_scalar_indices, 'CDP_Y'] *= absolute_scalar_value

        # when unpacking, if positive, to be used as a multiplier,
        # so here we divide
        positive_scalar_indices = self.table.COORDSC > 0

        self.table.loc[positive_scalar_indices, 'SOU_X'] /= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'SOU_Y'] /= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'REC_X'] /= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'REC_Y'] /= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'CDP_X'] /= absolute_scalar_value
        self.table.loc[positive_scalar_indices, 'CDP_Y'] /= absolute_scalar_value

        # since these headers have to be integers, we transform them
        self.table.loc[:, 'SOU_X'] = np.int64(self.table['SOU_X'].values)
        self.table.loc[:, 'SOU_Y'] = np.int64(self.table['SOU_Y'].values)
        self.table.loc[:, 'REC_X'] = np.int64(self.table['REC_X'].values)
        self.table.loc[:, 'REC_Y'] = np.int64(self.table['REC_Y'].values)
        self.table.loc[:, 'CDP_X'] = np.int64(self.table['CDP_X'].values)
        self.table.loc[:, 'CDP_Y'] = np.int64(self.table['CDP_Y'].values)
