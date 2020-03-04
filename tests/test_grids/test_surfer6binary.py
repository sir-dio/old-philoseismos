""" philoseismos: with passion for the seismic method.

This files contains tests for Surfer 6 Binary Grid object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import struct
import numpy as np
import pytest

from philoseismos.grids import Surfer6BinaryGrid


@pytest.fixture
def bad_grd_file(tmp_path_factory):
    """ A file without the needed ID string at the beginning."""

    tempdir = tmp_path_factory.mktemp('tempdir')
    file = tempdir / 'bad_file.grd'

    with open(file, 'bw') as f:
        bad_data = 'This is a very bad data!'.encode(encoding='cp500')
        f.write(bad_data)

    return file


@pytest.fixture(scope='module')
def grd_file(tmp_path_factory):
    """ A manually created .grf file to test. """

    tempdir = tmp_path_factory.mktemp('tempdir')
    file = tempdir / 'test.grd'

    # pack nx, ny, xlo, xhi, ylo, yhi, zlo, zhi
    format_string = '<hhdddddd'
    values = 10, 15, 0, 9, 10, 38, 0, 150
    packed_header = struct.pack(format_string, *values)

    # create the data to pack
    data = np.arange(150).reshape(15, 10)
    data_format_string = '<' + 'f' * 10

    with open(file, 'bw') as f:
        f.write(b'DSBB')  # id string
        f.write(packed_header)

        for row in data:
            packed = struct.pack(data_format_string, *row)
            f.write(packed)

    return file


def test_loading_surfer6binary(grd_file, bad_grd_file):
    """ Test loading process of the grid files. """

    # only proceeds to read true .grd files
    with pytest.raises(ValueError):
        grd = Surfer6BinaryGrid(bad_grd_file)

    grd = Surfer6BinaryGrid(grd_file)

    assert grd.nx == 10
    assert grd.ny == 15
    assert grd.xlo == 0
    assert grd.xhi == 9
    assert grd.ylo == 10
    assert grd.yhi == 38
    assert grd.zlo == 0
    assert grd.zhi == 150

    assert grd.DM.shape == (15, 10)
    assert np.alltrue(grd.DM == np.arange(150).reshape(15, 10))


def test_surfer6binary_properties(grd_file):
    """ Test the properties of the grid. """

    grd = Surfer6BinaryGrid(grd_file)

    # to help construct the plt.imshow, grid returns it's extent
    assert grd.extent == [0, 9, 38, 10]


def test_surfer6binary_ivert_axis_methods(grd_file):
    """ Test the .invert_yaxis() and .invert_xaxis() method of the gird. """

    grd = Surfer6BinaryGrid(grd_file)

    dm = np.arange(150).reshape(15, 10)

    assert np.alltrue(grd.DM == dm)
    assert grd.ylo == 10
    assert grd.yhi == 38
    assert grd.xhi == 9
    assert grd.xlo == 0
    grd.invert_yaxis()
    assert np.alltrue(grd.DM == dm[::-1, :])
    assert grd.ylo == 38
    assert grd.yhi == 10
    grd.invert_xaxis()
    assert np.alltrue(grd.DM == dm[::-1, ::-1])
    assert grd.xlo == 9
    assert grd.xhi == 0
    grd.invert_yaxis()
    assert np.alltrue(grd.DM == dm[:, ::-1])
    grd.invert_xaxis()
    assert np.alltrue(grd.DM == dm)
    assert grd.ylo == 10
    assert grd.yhi == 38
    assert grd.xhi == 9
    assert grd.xlo == 0
