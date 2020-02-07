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

    sgy.TFH.set_content('This is a test Textual File Header! :)')
    sgy.BFH['Job ID'] = 666
    sgy.DM.matrix += 12
    sgy.G.table.loc[12, 'SOU_X'] = 57

    sgy.save_file(path)

    return path
