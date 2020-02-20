""" philoseismos: with passion for the seismic method.

This file defines Surfer6BinaryGrid class, that reads Surfer 6 Binary Grid data format.

@author: Dubrovin Ivan
e-mail: dubrovin.io@icloud.com """

import struct

import numpy as np


class Surfer6BinaryGrid:

    def __init__(self, file=None):
        """ """

        self.nx = None
        self.ny = None
        self.xlo = None
        self.xhi = None
        self.ylo = None
        self.yhi = None
        self.zlo = None
        self.zhi = None

        self.DM = None

        if file:
            self.load_file(file)

    def load_file(self, file: str):
        """ Loads the specified file. """

        with open(file, 'br') as f:
            id_ = f.read(4)

            # first 4 bytes are ID string identifying a file as Surfer 6 Binary Grid
            if id_ != b'DSBB':
                raise ValueError('The specified file is not a Surfer 6 Binary grid!')

            self.nx = struct.unpack('<h', f.read(2))[0]  # number of grid lines along the X axis
            self.ny = struct.unpack('<h', f.read(2))[0]  # number of grid lines along the Y axis
            self.xlo = struct.unpack('<d', f.read(8))[0]  # minimum X value of the grid
            self.xhi = struct.unpack('<d', f.read(8))[0]  # maximum X value of the grid
            self.ylo = struct.unpack('<d', f.read(8))[0]  # minimum Y value of the grid
            self.yhi = struct.unpack('<d', f.read(8))[0]  # maximum Y value of the grid
            self.zlo = struct.unpack('<d', f.read(8))[0]  # minimum Z value of the grid
            self.zhi = struct.unpack('<d', f.read(8))[0]  # maximum Z value of the grid

            # a matrix to hold the data
            self.DM = np.empty(shape=(self.ny, self.nx), dtype=np.float64)

            # now read the rows. each row has a constant Y coordinate.
            # first row corresponds to ylo, last row corresponds to yhi.
            # within each row Z values are ordered from xlo to xhi

            format_string = '<' + 'f' * self.nx

            for row in range(self.ny):
                bytes_ = f.read(self.nx * 4)
                values = struct.unpack(format_string, bytes_)
                self.DM[row, :] = values

    @property
    def extent(self):
        return [self.xlo, self.xhi, self.ylo, self.yhi]

    @property
    def format_kwargs(self):
        return {
            'aspect': 'auto',
            'extent': self.extent,
        }
