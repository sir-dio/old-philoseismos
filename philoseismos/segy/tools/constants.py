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

BFH_columns = ['Sample interval',  # mandatory
               'Sample format',    # mandatory
               'Samples / trace',  # mandatory
               '# Traces',
               'Job ID',
               'Line #',
               'Data offset',
               '# Ext. TFHs',
               'SEG-Y Revision Major',
               'SEG-Y Revisiom Minor',
               ]

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
