""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

from philoseismos.segy.tools.constants import sample_format_codes as sfc

import struct


# ----- Getting values ----- #

def get_endianness(file):
    """ Returns endianness of the SEG-Y file.

    Returns '>' for big and '<' for little endian.

    Grabs the bytes that encode the Sample Format code in the
    Binary File Header from the specified file, and checks whether big or
    little endian give the value that corresponds to sample format codes
    described in SEG-Y file format description.

    """

    sf_bytes = _get_sample_format_bytes(file)

    try:
        assert 16 > struct.unpack('>h', sf_bytes)[0]
        return '>'
    except AssertionError:
        return '<'


def get_sample_format(file):
    """ Returns a tuple (sample size, format letter for srtuct, verbose description). """

    endian = get_endianness(file)
    sf_bytes = _get_sample_format_bytes(file)
    sf = struct.unpack(endian + 'h', sf_bytes)[0]

    return sfc[sf]


def get_sample_interval(file):
    """ Returns Sample Interval of specified file in microseconds. """

    endian = get_endianness(file)

    with open(file, 'br') as f:
        f.seek(3216)
        si_bytes = f.read(2)

    return struct.unpack(endian + 'h', si_bytes)[0]


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

def _get_sample_format_bytes(file):
    """ Returns bytes corresponding to Sample Format code from the file. """

    with open(file, 'br') as f:
        f.seek(3224)
        return f.read(2)
