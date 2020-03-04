""" philoseismos: with passion for the seismic method.

This file is a collection of constants that are used in different parts
of the philoseismos.segy package.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import numpy as np

# a dictionary that maps sample format codes from BFH
# to the sample size, formatting letter for packing/unpacking,
# and a verbose description:
sample_format_codes = {
    1: (4, None, '4-byte IBM floating-point'),
    2: (4, 'i', '4-byte signed integer'),
    3: (2, 'h', '2-byte signed integer'),
    5: (4, 'f', '4-byte IEEE floating-point'),
    6: (4, 'd', '8-byte IEEE floating-point'),
    8: (1, 'b', '1-byte signed integer'),
    9: (8, 'q', '8-byte signed integer'),
    10: (4, 'L', '4-byte, unsigned integer'),
    11: (2, 'H', '2-byte, unsigned integer'),
    12: (8, 'Q', '8-byte, unsigned integer'),
    16: (1, 'B', '1-byte, unsigned integer')
}

# strings to unpack a BFH from bytes to tuples using struct.unpack():
BFH_format_string = 'iiihhhhhhhhhhhhhhhhhhhhhhhhiiiQQiii'  # first 100 bytes
BFH_format_string += 'i' * 50  # unassigned bytes
BFH_format_string += 'BBhhihQQi'  # bytes from 300 to 332
BFH_format_string += 'i' * 17  # more unassigned bytes

# a list of column names that are used when BFHs are created
BFH_columns = ['Job ID',
               'Line #',
               'Reel #',
               'Traces / Ensemble',
               'Aux. Traces / Ensemble',
               'Sample Interval',
               'Sample Interval (orig.)',
               'Samples / Trace',
               'Samples / Trace (orig.)',
               'Sample Format',
               'Ensemble Fold',
               'Trace Sorting',
               'Vertical Sum',
               'Sweep Freq. (start)',
               'Sweep Freq. (end)',
               'Sweep Length',
               'Sweep Type',
               'Sweep Channel',
               'Sweep Taper (start)',
               'Sweep Taper (end)',
               'Taper Type',
               'Correlated Flag',
               'Binary Gain Recovered Flag',
               'Amp. Recovery Method',
               'Measurement System',  # 1 for meters, 2 for feet
               'Impulse Polarity',
               'Vibratory Polarity',
               'Ext. Traces / Ensemble',
               'Ext. Aux. Traces / Ensemble',
               'Ext. Samples / Trace',
               'Ext. Sample Interval',
               'Ext. Sample Interval (orig.)',
               'Ext. Sample / Trace (orig.)',
               'Ext. Ensemble Fold',
               'Integer Constant']

BFH_columns += [f'Unassigned {i + 1}' for i in range(50)]

BFH_columns += ['SEG-Y Rev. Major',
                'SEG-Y Rev. Minor',
                'Fixed Trace Length Flag',
                '# Ext. TFHs',
                '# Additional Trace Headers',
                'Time Basis',
                '# Traces',
                'Byte Offset of Data',
                '# Trailer Stanzas']

BFH_columns += [f'Unassigned {i + 51}' for i in range(17)]

TH_format_string = 'iiiiiiihhhhiiiiiiiihhiiiihhhhhhhhhhhhhhhhhhhhhhhhhh'
TH_format_string += 'hhhhhhhhhhhhhhhhhhhhiiiiihhihhhhhhhhihh'
# then 8 bytes of text (ASCII or EBCDIC)

# TODO: A helper function explaining the headers.
# TODO A helper function explaining the BFH fields.

# a list that contains names of trace headers that are used
# to create a geometry DataFrame in the Data object
TH_columns = ['TRACENO',  # ordinal number of a trace
              'Trace No. (file)',
              'FFID',  # unique number of a shot
              'CHAN',  # channel number
              'SOURCE',  # number of a source point
              'CDP',  # number of a common depth point
              'SEQNO',  # ordinal number of a trace in the ensemble
              'TRC_TYPE',  # ID code for a trace
              'STACKCNT',  # number of vertically stacked traces
              'TRFOLD',  # number of horizontally stacked traces
              'Data Use',
              'OFFSET',  # offset - distance between the source and the receiver
              'REC_ELEV',  # receiver elevation
              'SOU_ELEV',  # source elevation
              'DEPTH',  # source depth from the surface
              'REC_DATUM',  # elevation of the datum at the receiver
              'SOU_DATUM',  # elevation of the datum at the source
              'SOU_H2OD',  # water depth at the source
              'REC_H2OD',  # water depth at the receiver
              'ELEVSC',  # scalar to apply to the elevations
              'COORDSC',  # scalar to apply to the coordinates
              'SOU_X',
              'SOU_Y',
              'REC_X',
              'REC_Y',
              'Coordinate Units',
              'Weathering Velocity',
              'Subweathering Velocity',
              'UPHOLE',  # vertical time at the source, ms
              'REC_UPHOLE',  # vertical time at the receiver, ms
              'SOU_STAT',  # a static correction at the source, ms
              'REC_STAT',  # a static correction at the receiver, ms
              'TOT_STAT',  # total static correction, ms
              'Lag Time A',
              'Lag Time B',
              'Delay Recording Time',
              'TLIVE_S',  # starting time of muting, ms
              'TFULL_S',  # ending time of muting, ms
              'NUMSMP',  # number of samples in a trace (RadExPro needs this!)
              'DT',  # sample interval in microseconds (RadExPro needs this!)
              'IGAIN',  # code of the gain type of the instrument
              'PREAMP',  # amplification coeefitient for instrument, dB
              'EARLYG',  # initial amplification of the instrument, dB
              'COR_FLAG',  # correlation flag (1 - no, 2 - yes)
              'SWEEPFREQSTART',  # starting frequency of the sweep, Hz
              'SWEEPFREQEND',  # ending frequency of the sweep, Hz
              'SWEEPLEN',  # length of the sweep, ms
              'SWEEPTYPE',  # code for the sweep type
              'Sweep Taper (start)',
              'Sweep Taper (end)',
              'Taper Type',
              'AAXFILT',  # frequency of the anti-aliasing filter, Hz
              'AAXSLOP',  # slope of the anti-aliasing filter, dB / oct
              'FREQXN',  # frequency of the reject filter, Hz
              'FXNSLOP',  # slope of the reject filter, dB / oct
              'FREQXL',  # low-cut frequency, Hz
              'FREQXH',  # high-cut frequency, Hz
              'FXLSLOP',  # low-cut slope, dB / oct
              'FXHSLOP',  # high-cut slope, dB / oct
              'YEAR',
              'DAY',
              'HOUR',
              'MINUTE',
              'SECOND',
              'Time Basis',
              'Weighting Factor',
              'Group No. of Roll Switch',
              'Group No. of First Trace',
              'Group No. of Last Trace',
              'Gap Size',
              'Over Travel',
              'CDP_X',
              'CDP_Y',
              'In-line No.',
              'Cross-line No.',
              'Shotpoint Number',
              'Shotpoint Scalar',
              'Trace Measurement Unit',
              'Transduction Constant (mantissa)',
              'Transduction Constant (10 power exponent)',
              'Transduction Units',
              'Device/Trace ID',
              'Times Scalar',
              'Source Type/Orientation',
              'Source Energy Direction (vertical)',
              'Source Energy Direction (cross-line)',
              'Source Energy Direction (in-line)',
              'Source Measurement (mantissa)',
              'Source Measurement (10 power exponent)',
              'Source Measurement Unit']
# then go 8 byte of a "Header name" - ASCII or EBCID

# a dictionary that maps sample format codes from BFH
# to the numpy.dtype for DataMatrix
data_type_map1 = {1: np.float64,
                  2: np.int32,
                  3: np.int16,
                  5: np.float32,
                  6: np.float64,
                  8: np.int8,
                  9: np.int64,
                  10: np.uint32,
                  11: np.uint16}

# a dictionary that maps the dtype of the matrix to
# the sample format code for BFH
data_type_map2 = {np.float32: 5,
                  np.int32: 2,
                  np.int16: 3,
                  np.float64: 6,
                  np.int8: 8,
                  np.int64: 9,
                  np.uint32: 10,
                  np.uint16: 11}

unpack_pbar_params = {
    'desc': 'Unpacking traces: ',
    'unit': ' tr',
}

pack_pbar_params = {
    'desc': 'Packing traces: ',
    'unit': ' tr',
}
