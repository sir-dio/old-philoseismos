""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

from philoseismos.coordinates import constants as const

import pandas as pd
import numpy as np


class WayPoints:
    """ This object represents a .wpt file, used in OziExplorer.

    The file format is described in the OziExplorer documentation.
    All information is stored in the pd.DataFrame.

    """

    def __init__(self, file=None):
        self.table = pd.DataFrame(index=range(1), columns=const.wpt_columns)
        self.table.fillna(0, inplace=True)

        self.version = 'OziExplorer Waypoint File Version 1.1'
        self.datum = 'WGS84'

        if file:
            self.load_from_file(file)

    # ----- Loading and writing ----- #

    def load_from_file(self, file):
        """ Loads a .wpt file into self. """

        with open(file, 'r') as f:
            self.version = f.readline().strip()
            self.datum = f.readline().strip()

        self.table = pd.read_csv(file, skiprows=4, skipinitialspace=True, names=const.wpt_columns)

    def save_to_file(self, file):
        """ Saves a .wpt file. """

        with open(file, 'w') as f:
            f.write(self.version + '\n')  # first line is file type and version information
            f.write(self.datum + '\n')  # second line is geodetic datum used for the lat/lon positions
            f.write('Reserved 2\n\n')  # third and fourth lines are reserved for future use

        self.table.to_csv(file, mode='a', header=False, index=False)

    # ----- Working with other file formats ----- #

    def import_sputnik_csv(self, file):
        """ Loads a .csv file generated in SPUTNIK software.

        SPUTNIK is differential GPS RTK survey control system.
        Use the default template when exporting SPUTNIK points from the app!

        The default .csv layout for export is as follows:
        Point name, point code, North, East, Mark (?), Latitude, Longitude,
        Altitude, Coord. Precision, Alt. Precision, PDOP (?), Solution type.

        """

        csv = pd.read_csv(file, names=const.sputnik_csv_columns)
        N = csv.shape[0]

        self.table = pd.DataFrame(index=range(N), columns=const.wpt_columns)

        self.table.loc[:, 'No.'] = range(1, N + 1)
        self.table.loc[:, 'Name'] = csv.loc[:, 'Name']
        self.table.loc[:, 'Latitude'] = csv.loc[:, 'Lat']
        self.table.loc[:, 'Longitude'] = csv.loc[:, 'Lon']
        self.table.loc[:, 'Date'] = 0
        self.table.loc[:, 'GPS Symbol'] = 0
        self.table.loc[:, 'Status'] = 1
        self.table.loc[:, 'Map display format'] = 3  # 1 is name only, 3 is name with dot
        self.table.loc[:, 'FG color'] = 0  # black
        self.table.loc[:, 'BG color'] = 65535  # yellow
        self.table.loc[:, 'Description'] = ''
        self.table.loc[:, 'Pointer direction'] = 0  # down
        self.table.loc[:, 'Garmin display format'] = 0
        self.table.loc[:, 'Proximity distance'] = csv.loc[:, 'Coord. Precision']
        self.table.loc[:, 'Altitude'] = csv.loc[:, 'Alt']
        self.table.loc[:, 'Font size'] = 6
        self.table.loc[:, 'Font style'] = 0  # not bold
        self.table.loc[:, 'Symbol size'] = 8
        self.table.loc[:, 'Proximity symbol position'] = 0
        self.table.loc[:, 'Proximity time'] = 0
        self.table.loc[:, 'Proximity or Route or Both'] = 2
        self.table.loc[:, 'File attachment name'] = np.nan
        self.table.loc[:, 'Proximity file attachment name'] = np.nan
        self.table.loc[:, 'Proximity symbol name'] = np.nan

    # ----- Dunder methods ----- #

    def __repr__(self):
        return str(self.table.loc[:, ['No.', 'Name', 'Latitude', 'Longitude', 'Altitude', 'Proximity Distance']])
