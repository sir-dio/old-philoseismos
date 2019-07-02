""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

from philoseismos.coordinates.constants import wpt_columns

import pandas as pd


class WayPoints:
    """ This object represents a .wpt file, used in OziExplorer.

    The file format is described in the OziExporer documentation.
    All information is stored in the """

    def __init__(self):
        self.table = None

        self.version = 'OziExplorer Waypoint File Version 1.1'
        self.datum = 'WGS84'

    # ----- Loading and writing ----- #

    def load_from_file(self, file):
        """ Loads a .wpt file into self. """

        with open(file, 'r') as f:
            self.version = f.readline().strip()
            self.datum = f.readline().strip()

        self.table = pd.read_csv(file, skiprows=4, skipinitialspace=True, names=wpt_columns)

    def save_to_file(self, file):
        """ Saves a .wpt file. """

        with open(file, 'w') as f:
            f.write(self.version + '\n')  # first line is file type and version information
            f.write(self.datum + '\n')  # second line is geodetic datum used for the lat/lon positions
            f.write('Reserved 2\n\n')  # third and fourth lines are reserved for future use

        self.table.to_csv(file, mode='a', header=False, index=False)

    # ----- Working with other file formats ----- #

    def import_csv(self, file):
        """ """

        pass
