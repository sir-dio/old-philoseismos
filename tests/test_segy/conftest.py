""" philoseismos: with passion for the seismic method.

This file contains tests for loading SEG-Y files with the Segy object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import pytest

from philoseismos import Segy


@pytest.fixture(scope='package')
def temporary_segy(tmp_path_factory):
    """ Returns a path to a temporary SEG-Y object to run tests on. """

    path = tmp_path_factory.mktemp('sgys') / 'test_segy.sgy'

    sgy = Segy.empty(shape=(48, 512), sample_interval=1000)

    # set up a Textual File Header
    sgy.TFH.set_content('This is a test Textual File Header! :)')

    # set up a Binary File Header
    sgy.BFH['Job ID'] = 666
    sgy.BFH['Line #'] = 69

    # set up a Data Matrix, which is zeros by default
    sgy.DM.matrix += 12

    # set up a Geometry
    sgy.G.table.loc[:, 'FFID'] = 1984
    sgy.G.table.loc[:, 'TRACENO'] = range(1, 49)
    sgy.G.table.loc[:, 'CHAN'] = range(1, 49)
    sgy.G.table.loc[:, 'SOU_X'] = range(50, 98)
    sgy.G.table.loc[:, 'REC_X'] = range(100, 148)
    sgy.G.table.loc[:, 'COORDSC'] = -1000

    sgy.G.table.loc[:, 'CDP_X'] = range(150, 198)
    sgy.G.table.loc[:, 'CDP_Y'] = range(250, 298)

    # the day I write this setup is February 11th, 2020
    sgy.G.table.loc[:, 'YEAR'] = 2020
    sgy.G.table.loc[:, 'DAY'] = 42
    sgy.G.table.loc[:, 'HOUR'] = 21
    sgy.G.table.loc[:, 'MINUTE'] = 31
    sgy.G.table.loc[:, 'SECOND'] = 38

    sgy.save_file(path)

    return path
