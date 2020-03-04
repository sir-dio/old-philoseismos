""" philoseismos: with passion for the seismic method.

This file contains tests for saving SEG-Y files with the Segy object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import struct
import numpy as np


# TODO: extend test to proper go through the file byte by byte


def test_tfh_is_written_correctly(temporary_segy):
    """ Test that TFH bytes are correct in the saved file. """

    with open(temporary_segy, 'br') as s:
        bytes_ = s.read(3200)

    assert bytes_ == 'This is a test Textual File Header! :)'.ljust(3200).encode('cp500')


def test_bfh_is_written_correctly(temporary_segy):
    """ Test that BFH bytes are correct in the saved file. """

    with open(temporary_segy, 'br') as s:
        # go to the start of the BFH
        s.seek(3200)

        assert s.read(4) == struct.pack('>i', 666)  # Job ID bytes
        assert s.read(4) == struct.pack('>i', 69)  # Line # bytes
        s.seek(3216)
        assert s.read(2) == struct.pack('>h', 1000)  # Sample Interval bytes
        s.seek(3220)
        assert s.read(2) == struct.pack('>h', 512)  # Sample / Trace bytes
        s.seek(3224)
        assert s.read(2) == struct.pack('>h', 5)  # Sample Format bytes


def test_geometry_is_written_correctly(temporary_segy):
    """ Test that Geometry bytes a correct in the saved file. """

    with open(temporary_segy, 'br') as s:
        # iterate over traces to check trace header bytes
        for i in range(48):
            # go to the start of the trace header
            s.seek(3600 + i * (240 + 512 * 4))
            assert s.read(4) == struct.pack('>i', i + 1)  # TRACENO bytes
            s.seek(4, 1)  # seek 4 bytes forward
            assert s.read(4) == struct.pack('>i', 1984)  # FFID bytes
            assert s.read(4) == struct.pack('>i', i + 1)  # CHAN bytes
            s.seek(54, 1)
            assert s.read(2) == struct.pack('>h', -1000)  # COORDSC bytes

            # the coordinates should be scaled appropriately
            assert s.read(4) == struct.pack('>i', (50 + i) * 1000)  # SOU_X bytes
            s.seek(4, 1)
            assert s.read(4) == struct.pack('>i', (100 + i) * 1000)  # REC_X bytes

            s.seek(30, 1)
            assert s.read(2) == struct.pack('>h', 512)  # NUMSMP bytes
            assert s.read(2) == struct.pack('>h', 1000)  # DT bytes

            s.seek(38, 1)
            assert s.read(2) == struct.pack('>h', 2020)  # YEAR bytes
            assert s.read(2) == struct.pack('>h', 42)  # DAY bytes
            assert s.read(2) == struct.pack('>h', 21)  # HOUR bytes
            assert s.read(2) == struct.pack('>h', 31)  # MINUTE bytes
            assert s.read(2) == struct.pack('>h', 38)  # SECOND bytes

            s.seek(14, 1)
            assert s.read(4) == struct.pack('>i', (150 + i) * 1000)  # CDP_X bytes
            assert s.read(4) == struct.pack('>i', (250 + i) * 1000)  # CDP_Y bytes


def test_data_matrix_is_written_correctly(temporary_segy):
    """ Test that Data Matrix bytes ar ecorrect in the saved file. """

    trace_format_string = '>' + 'f' * 512
    trace_values = np.ones(512) * 12
    what_trace_bytes_should_be = struct.pack(trace_format_string, *trace_values)

    with open(temporary_segy, 'br') as s:
        # iterate over traces
        for i in range(48):
            # go to the start of the trace
            s.seek(3840 + i * (240 + 512 * 4))
            assert s.read(512 * 4) == what_trace_bytes_should_be
