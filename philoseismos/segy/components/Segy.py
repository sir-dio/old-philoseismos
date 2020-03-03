""" philoseismos: with passion for the seismic method.

This file defines the most important object in the philoseismos.segy package:
the Segy object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy.components import TextualFileHeader, BinaryFileHeader
from philoseismos.segy.components import DataMatrix, Geometry
from philoseismos.segy.tools.constants import sample_format_codes as sfc
from philoseismos.segy.tools import ibm
from philoseismos.segy.tools.constants import TH_format_string, TH_columns, pack_pbar_params
from philoseismos.segy.tools import general_functions as gfunc

import struct
import numpy as np
import pandas as pd
from tqdm import tqdm


class Segy:
    """ Object that represents a SEG-Y file.

    Fathers all the components: Textual and Binary Headers, DataMatrix, Geometry.

    """

    def __init__(self, file=None, progress=False):
        """ Creates an empty Segy object.

        If file is specified, loads the contents from that file.

        """

        self.file = file

        self.TFH = TextualFileHeader()
        self.BFH = BinaryFileHeader()
        self.DM = DataMatrix()
        self.G = Geometry()

        if file:
            self.load_file(file, progress=progress)

    # ----- Loading and writing ----- #

    def load_file(self, file, progress=False):
        """ Loads specified .sgy file into self. """

        self.TFH.load_from_file(file)
        self.BFH.load_from_file(file)
        self.DM.load_from_file(file, progress=progress)
        self.G.load_from_file(file)

    def save_file(self, file, endian='>', progress=False):
        """ Saves self into a specified .sgy file. """

        ss, fl, _ = sfc[self.BFH['Sample Format']]
        nt, tl = self.DM.matrix.shape

        self.BFH._update_bytes(endian)
        self.G._apply_coordinates_scalar_before_packing()

        with open(file, 'bw') as f:
            f.write(self.TFH._bytes)
            f.write(self.BFH._bytes)

            if not fl:  # IBM
                if progress:
                    with tqdm(total=nt, **pack_pbar_params) as pbar:
                        for i in range(nt):
                            raw_header = bytearray(240)
                            raw_header[:232] = struct.pack(endian + TH_format_string, *self.G.table.loc[i, :].values)
                            f.write(raw_header)

                            raw_trace = ibm.pack_ibm32_series(endian, self.DM.matrix[i])
                            f.write(raw_trace)
                            pbar.update(1)
                else:
                    for i in range(nt):
                        raw_header = bytearray(240)
                        raw_header[:232] = struct.pack(endian + TH_format_string, *self.G.table.loc[i, :].values)
                        f.write(raw_header)

                        raw_trace = ibm.pack_ibm32_series(endian, self.DM.matrix[i])
                        f.write(raw_trace)
            else:
                format_string = endian + fl * tl
                if progress:
                    with tqdm(total=nt) as pbar:
                        for i in range(nt):
                            raw_header = bytearray(240)
                            raw_header[:232] = struct.pack(endian + TH_format_string, *self.G.table.loc[i, :].values)
                            f.write(raw_header)

                            raw_trace = struct.pack(format_string, *self.DM.matrix[i])
                            f.write(raw_trace)
                            pbar.update(1)
                else:
                    for i in range(nt):
                        raw_header = bytearray(240)
                        raw_header[:232] = struct.pack(endian + TH_format_string, *self.G.table.loc[i, :].values)
                        f.write(raw_header)

                        raw_trace = struct.pack(format_string, *self.DM.matrix[i])
                        f.write(raw_trace)

        self.G._apply_coordinate_scalar_after_unpacking()

    # ----- Extracting parts ----- #

    # TODO: empty and empty_like should fill the TRACENO header

    def extract_by_fixed_headers(self, fixed_headers):
        """ Returns a new Segy object, whose data is a subset based on given fixed headers.

         Args:
             fixed_headers: Dictionary of format {header name 1: fixed value 1, ...}

         """

        extracted_g = self.G.table.copy()
        for key, value in fixed_headers.items():
            extracted_g = extracted_g.loc[extracted_g[key] == value]

        extracted_dm = self.DM.matrix[extracted_g.index]

        out = Segy.empty_like(self)

        out.TFH = self.TFH
        out.BFH = self.BFH
        out.DM.matrix = extracted_dm
        out.G.table = extracted_g.reset_index(drop=True)

        out.BFH.table['Traces / Ensemble'] = extracted_dm.shape[0]

        return out

    # ----- Factory Methods ----- #

    @classmethod
    def empty_like(cls, segy):
        """ Returns an empty Segy with same parameters as the specified file.

        Args:
            segy: Segy object or path to the file.

        """

        # TODO: add a test case for this.

        out = cls()

        out.TFH.set_content('Created in philoseismos! With love to programming and seismology.')

        if isinstance(segy, str):
            nt = gfunc.get_number_of_traces(segy)
            si = gfunc.get_sample_interval(segy)
            ns = gfunc.get_trace_length(segy)

            out.BFH['Traces / Ensemble'] = nt
            out.BFH['Sample Interval'] = si
            out.BFH['Samples / Trace'] = ns
            out.BFH['Sample Format'] = 5

            out.DM.matrix = np.zeros((nt, ns), dtype=np.float32)
            out.DM.dt = ns * si / 1e3
            out.DM.t = np.arange(0, out.DM.dt, out.DM.dt)

            out.G.table = pd.DataFrame(index=range(nt), columns=TH_columns)
            out.G.table.loc[:, 'FFID'] = 1
            out.G.table.loc[:, 'CHAN'] = range(1, nt + 1)
            out.G.table.loc[:, 'DT'] = int(si)
            out.G.table.loc[:, 'NUMSMP'] = ns
            out.G.table.fillna(0, inplace=True)
        elif isinstance(segy, Segy):
            shape = segy.DM.matrix.shape
            out.DM.matrix = np.zeros(shape, dtype=np.float32)

            out.BFH['Traces / Ensemble'] = shape[0]
            out.BFH['Sample Interval'] = segy.BFH['Sample Interval']
            out.BFH['Samples / Trace'] = segy.BFH['Samples / Trace']
            out.BFH['Sample Format'] = 5

            out.DM.dt = out.BFH['Sample Interval'] / 1e3
            out.DM.t = np.arang(0, shape[0] * out.DM.dt, out.DM.dt)

            out.G.table = pd.DataFrame(index=range(shape[0]), columns=TH_columns)
            out.G.table.loc[:, 'FFID'] = 1
            out.G.table.loc[:, 'CHAN'] = range(1, shape[0] + 1)
            out.G.table.loc[:, 'DT'] = int(segy.BFH['Sample Interval'])
            out.G.table.loc[:, 'NUMSMP'] = segy.BFH['Samples / Trace']
            out.G.table.fillna(0, inplace=True)
        else:
            raise ValueError('The `segy` parameter has to be either a Segy object or a string')

        return out

    @classmethod
    def empty(cls, shape=(24, 1024), sample_interval=500):
        """ Returns an empty Segy with the given Data Matrix shape. """

        # TODO: add a test case for this.

        out = cls()

        out.TFH.set_content('Created in philoseismos! With love to programming and seismology.')

        out.BFH.table['Traces / Ensemble'] = shape[0]
        out.BFH.table['Sample Interval'] = int(sample_interval)
        out.BFH.table['Samples / Trace'] = shape[1]
        out.BFH.table['Sample Format'] = 5

        out.DM.matrix = np.zeros(shape, dtype=np.float32)
        out.DM.dt = sample_interval / 1e3
        out.DM.t = np.arange(0, shape[1] * out.DM.dt, out.DM.dt)

        out.G.table = pd.DataFrame(index=range(shape[0]), columns=TH_columns)
        out.G.table.loc[:, 'FFID'] = 1
        out.G.table.loc[:, 'CHAN'] = range(1, shape[0] + 1)
        out.G.table.loc[:, 'DT'] = int(sample_interval)
        out.G.table.loc[:, 'NUMSMP'] = shape[1]
        out.G.table.fillna(0, inplace=True)

        return out
