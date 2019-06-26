""" philoseismos: with passion for the seismic method.

@author: sir-dio
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

trace_header_str = 'iiiiiiihhhhiiiiiiiihhiiiihhhhhhhhhhhhhhhhhhhhhhhhhh'
trace_header_str += 'hhhhhhhhhhhhhhhhhhhhiiiiihhihhhhhhhhihh'
# then 8 bytes of text (ASCII or EBCDIC)

# a list that contains names of trace headers that are used
# to create a geometry DataFrame in the Data object
trace_header_columns = ['TRACENO',  # unique number of a trace
                        'Trace No. (file)',
                        'FFID',  # unique number of the shot
                        'CHAN',  # channel number
                        'Energy Source No.',
                        'CDP',
                        'Trace No. (ensemble)',
                        'Trace ID',
                        '# Vertically Summed Traces',
                        '# Horizontally Stacked Traces',
                        'Data Use',
                        'OFFSET',
                        'Receiver Elevation',
                        'Source Elevation',
                        'Source Depth',
                        'Receiver Datum Elevation',
                        'Source Datum Elevation',
                        'Water Column Height at Source',
                        'Water Column Height at Receiver',
                        'ELEVSC',
                        'COORDSC',
                        'SOU_X',
                        'SOU_Y',
                        'REC_X',
                        'REC_Y',
                        'Coordinate Units',
                        'Weathering Velocity',
                        'Subweathering Velocity',
                        'Uphole Time at Source',
                        'Uphole Time at Receiver',
                        'Source Static Correction',
                        'Receiver Static Correction',
                        'Total Static',
                        'Lag Time A',
                        'Lag Time B',
                        'Delay Recording Time',
                        'Mute Time (start)',
                        'Mute Time (end)',
                        '# Samples',
                        'Sample Interval',
                        'Gain Type',
                        'Instrument Gain Constant',
                        'Instrument Initial Gain',
                        'Correlated Flag',
                        'Sweep Freq. (start)',
                        'Sweep Freq. (end)',
                        'Sweep Length',
                        'Sweep Type',
                        'Sweep Taper (start)',
                        'Sweep Taper (end)',
                        'Taper Type',
                        'Alias Filter Freq.',
                        'Alias Filter Slope',
                        'Notch Filter Freq.',
                        'Notch Filter Slope',
                        'Low-cut Freq.',
                        'High-cut Freq.',
                        'Low-cut Slope',
                        'High-cut Slope',
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
# then a 'Header Name' -> 8 byte of text (ASCII or EBCDIC)

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
