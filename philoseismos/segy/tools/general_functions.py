""" philoseismos: with passion for the seismic method.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy.tools.constants import sample_format_codes as sfc

import struct
import os.path


# ----- Getting values ----- #

def get_endianness(file):
    """ Returns endianness of the SEG-Y file.

    Returns '>' for big and '<' for little endian.

    Grabs the bytes that encode the Sample Format code in the
    Binary File Header from the specified file, and checks whether big or
    little endian give the value that corresponds to sample format codes
    described in SEG-Y file format description.

    """

    with open(file, 'br') as f:
        f.seek(3224)
        sf_bytes = f.read(2)

    return _detect_endianness_from_sample_format_bytes(sf_bytes)


def get_sample_format(file):
    """ Returns a tuple (sample size, format letter for srtuct, verbose description). """

    with open(file, 'br') as f:
        f.seek(3224)
        sf_bytes = f.read(2)

    endian = _detect_endianness_from_sample_format_bytes(sf_bytes)
    sf = struct.unpack(endian + 'h', sf_bytes)[0]

    return sfc[sf]


def get_sample_interval(file):
    """ Returns Sample Interval of specified file in microseconds. """

    with open(file, 'br') as f:
        f.seek(3216)
        si_bytes = f.read(2)
        f.seek(3224)
        sf_bytes = f.read(2)

    endian = _detect_endianness_from_sample_format_bytes(sf_bytes)

    return struct.unpack(endian + 'h', si_bytes)[0]


def get_trace_length(file):
    """ Returns trace length in specified file in samples. """

    with open(file, 'br') as f:
        f.seek(3220)
        tl_bytes = f.read(2)
        f.seek(3224)
        sf_bytes = f.read(2)

    endian = _detect_endianness_from_sample_format_bytes(sf_bytes)

    return struct.unpack(endian + 'h', tl_bytes)[0]


def get_number_of_traces(file):
    """ Returns the number of traces in the file.

    If the value in the BFH is not specified, it is calculated
    by dividing size of the Data section of the file by the size
    of one trace.

    """

    with open(file, 'br') as f:
        f.seek(3224)
        sf_bytes = f.read(2)
        f.seek(3512)
        nt_bytes = f.read(8)

    endian = _detect_endianness_from_sample_format_bytes(sf_bytes)
    number = struct.unpack(endian + 'Q', nt_bytes)[0]

    return number if number != 0 else _calculate_number_of_traces(file)


# ----- Getting values with a little interpretation ----- #

def get_trace_length_in_ms(file):
    """ Returns trace length in specified file in milliseconds. """

    with open(file, 'br') as f:
        f.seek(3216)
        si_bytes = f.read(2)
        f.seek(3220)
        tl_bytes = f.read(2)
        f.seek(3224)
        sf_bytes = f.read(2)

    endian = _detect_endianness_from_sample_format_bytes(sf_bytes)
    trace_length = struct.unpack(endian + 'h', tl_bytes)[0]
    sample_interval = struct.unpack(endian + 'h', si_bytes)[0]

    return (trace_length - 1) * sample_interval / 1000


def get_sample_frequency(file):
    """ Returns sample frequency of specified files in Herz. """

    sample_interval = get_sample_interval(file)

    return 1e6 / (sample_interval)


# ----- Checking boolean values ----- #

def check_fixed_trace_length_flag(file):
    """ Returns True if Fixed Trace Length flag is activated.

    This indicates that all traces in this SEG-Y
    file are guaranteed to have the same sample interval, number of trace header
    blocks and trace samples, as specified in Binary File Header.

    """

    endian = get_endianness(file)

    with open(file, 'br') as f:
        f.seek(3502)
        ftlf_bytes = f.read(2)

    return True if struct.unpack(endian + 'h', ftlf_bytes) == 1 else False


# ----- Setting values ----- #

def set_sample_format(file, value):
    """ Set the Sample Format in the file to the specified value.

    Note: The Binary File Header will be changed. Be careful to change
    such an important parameter!

    """

    endian = get_endianness(file)

    with open(file, 'br+') as f:
        f.seek(3224)
        f.write(struct.pack(endian + 'h', value))


def set_sample_interval(file, value):
    """ Set the Sample Interval in the file to the specified value.

    Note: The Binary File Header will be changed. Be careful to change
    such an important parameter!

    """

    endian = get_endianness(file)

    with open(file, 'br+') as f:
        f.seek(3216)
        f.write(struct.pack(endian + 'h', value))


# ----- Internal functions ----- #

def _detect_endianness_from_sample_format_bytes(sample_format_bytes):
    """ Returns endianness detected from Sample Format bytes.

    Takes in two bytes that correspond to Sample Format code,
    and checks which endianness yields values defined
    in SEG-Y revision document.

    """

    try:
        assert 16 > struct.unpack('>h', sample_format_bytes)[0]
        return '>'
    except AssertionError:
        return '<'


def _calculate_number_of_traces(file):
    """ Returns calculated number of traces. """

    file_size = os.path.getsize(file)
    data_size = file_size - 3600  # exclude Textual and Binary file headers

    with open(file, 'br') as f:
        f.seek(3220)
        tl_bytes = f.read(2)
        f.seek(3224)
        sf_bytes = f.read(2)

    endian = _detect_endianness_from_sample_format_bytes(sf_bytes)

    trace_length = struct.unpack(endian + 'h', tl_bytes)[0]
    sf = struct.unpack(endian + 'h', sf_bytes)[0]
    sample_size, _, _ = sfc[sf]

    trace_size = trace_length * sample_size

    return int(data_size / (trace_size + 240))  # each trace has a 240 byte header
