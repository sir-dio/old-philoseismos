""" philoseismos: with passion for the seismic method.

This file contains tests for loading SEG-Y files with the Segy object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import numpy as np

from philoseismos.segy.components import TextualFileHeader, BinaryFileHeader, DataMatrix, Geometry


def test_tfh_loads_correctly(temporary_segy):
    """ Test the loading of the Textual File Header. """

    tfh = TextualFileHeader()
    tfh.load_from_file(temporary_segy)

    assert tfh.text == 'This is a test Textual File Header! :)'.ljust(3200)


def test_bfh_loads_correctly(temporary_segy):
    """ Test loading of the Binary File Header. """

    bfh = BinaryFileHeader()
    bfh.load_from_file(temporary_segy)

    assert bfh['Sample Interval'] == 1000
    assert bfh['Samples / Trace'] == 512
    assert bfh['Sample Format'] == 5
    assert bfh['Traces / Ensemble'] == 48
    assert bfh['Job ID'] == 666
    assert bfh['Line #'] == 69


def test_data_matrix_loads_correctly(temporary_segy):
    """ Test loading of the Data Matrix. """

    dm = DataMatrix()
    dm.load_from_file(temporary_segy)

    assert np.alltrue(dm.matrix == np.ones(48 * 512).reshape(48, 512) * 12)


def test_geometry_loads_correctly(temporary_segy):
    """ Test loading of the Geometry. """

    g = Geometry()
    g.load_from_file(temporary_segy)

    assert g.table.loc[0, 'FFID'] == 1984
    assert g.table.loc[11, 'FFID'] == 1984
    assert g.table.loc[47, 'FFID'] == 1984
    assert g.table.loc[0, 'CHAN'] == 1
    assert g.table.loc[11, 'CHAN'] == 12
    assert g.table.loc[47, 'CHAN'] == 48
    assert g.table.loc[0, 'COORDSC'] == -1000
    assert g.table.loc[11, 'COORDSC'] == -1000
    assert g.table.loc[47, 'COORDSC'] == -1000
    assert g.table.loc[0, 'SOU_X'] == 50
    assert g.table.loc[11, 'SOU_X'] == 61
    assert g.table.loc[47, 'SOU_X'] == 97
    assert g.table.loc[0, 'REC_X'] == 100
    assert g.table.loc[11, 'REC_X'] == 111
    assert g.table.loc[47, 'REC_X'] == 147
