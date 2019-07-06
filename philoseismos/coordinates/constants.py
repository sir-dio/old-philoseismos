""" philoseismos: with passion for the seismic method.

This file contains a collection of constants that are used throughout the
philoseismos.coordinates package.

@author: Dubrovin Ivan
e-mail: dubrovin.io@icloud.com """

wpt_columns = [  # the comments are from the OziExplorer documentation
    'No.',
    'Name',
    'Latitude',  # in decimal degrees
    'Longitude',  # in decimal degrees
    'Date',  # some weird format
    'GPS Symbol',  # 0 to number of symbols in GPS
    'Status',  # always set to 1, for some reason
    'Map display format',
    'FG color',  # RGB value
    'BG color',  # RGB value
    'Description',  # 40 characters max, no commas
    'Pointer direction',
    'Garmin display format',
    'Proximity distance',  # 0 is off, any other number is valid
    'Altitude',  # in feet
    'Font size',  # in points
    'Font style',  # 0 is normal, 1 is bold
    'Symbol size',  # 17 is normal size
    'Proximity symbol position',
    'Proximity time',
    'Proximity or Route or Both',
    'File attachment name',
    'Proximity file attachment name',
    'Proximity symbol name'
]

sputnik_csv_columns = [
    'Name',
    'Code',
    'N',
    'E',
    'Mark',
    'Lat',
    'Lon',
    'Alt',
    'Coord. Precision',
    'Alt. Precision',
    'PDOP',
    'Solution type'
]
