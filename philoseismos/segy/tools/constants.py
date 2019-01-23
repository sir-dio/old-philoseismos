import numpy as np

# a dictionary that maps sample format codes from BFHs
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

# strings to unpack a BFHs from bytes to tuples:
bfh_string1 = 'iiihhhhhhhhhhhhhhhhhhhhhhhhiiiQQiii'  # first 100 bytes
bfh_string2 = 'BBhhihQQi'  # bytes from 300 to 332

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
               'Integer Constant',
               'SEG-Y Rev. Major',
               'SEG-Y Rev. Minor',
               'Fixed Trace Length Flag',
               '# Ext. TFHs',
               '# Additional Trace Headers',
               'Time Basis',
               '# Traces',
               'Byte Offset of Data',
               '# Trailer Stanzas']

# a list that contains names of trace header that are used
# to create a geometry DataFrame in the Data object
trace_header_list = ['TRACENO',
                     'FFID',
                     'CHAN',
                     'SOU_X',
                     'SOU_Y',
                     'REC_X',
                     'REC_Y',
                     'CDP_X',
                     'CDP_Y',
                     'CDP',
                     'YEAR',
                     'DAY',
                     'HOUR',
                     'MINUTE',
                     'SECOND',
                     'OFFSET',
                     'ELEVSC',
                     'COORDSC',
                     'dt',
                     '_trace',
                     ]

# a dictionary that maps the dtype of the matrix to
# the sample format code for BFH
data_type_map = {np.dtype('float32'): 5,
                 np.dtype('int32'): 2,
                 np.dtype('int16'): 3,
                 np.dtype('float64'): 6,
                 np.dtype('int8'): 8,
                 np.dtype('int64'): 9,
                 np.dtype('uint32'): 10,
                 np.dtype('uint16'): 11}
