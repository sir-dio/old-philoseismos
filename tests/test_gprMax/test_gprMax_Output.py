""" philoseismos: with passion for the seismic method.

This file contains tests for the grpMax.Output object.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

import pytest
import h5py
import numpy as np

from philoseismos.gprMax import Output

# a dictionary containing root attributes for the output file
output_file_attrs = {
    'Iterations': 100,
    'Title': 'Manually created output',
    'dt': 1e-12,
    'dx_dy_dz': [0.01, 0.01, 0.01],
    'gprMax': '3.1.5',
    'nrx': 1,
    'nsrc': 1,
    'nx_ny_nz': [100, 100, 1],
    'rxsteps': [2, 0, 0],
    'srcsteps': [2, 0, 0],
}

# a dictionary containing the datasets for the output file
output_file_data = {
    'Ex': np.ones(100),
    'Ey': np.ones(100) * 2,
    'Ez': np.ones(100) * 3,
    'Hx': np.ones(100) * 4,
    'Hy': np.ones(100) * 5,
    'Hz': np.ones(100) * 6,
}


@pytest.fixture(scope='module')
def sigle_Ascan(tmpdir_factory):
    """ A hand-made simulation of gprMax output. """

    # set up a temporary directory and a temporary file within
    tempdir = tmpdir_factory.mktemp('tempdir')
    file = tempdir / 'gprMax.out'

    # write the hand-made output to the temporary file
    _write_example_output_into(file, rx_coord=[0.5, 0.5, 0], src_coord=[0.5, 0.5, 0])

    return file


@pytest.fixture(scope='module')
def basename_of_series_of_Ascans(tmpdir_factory):
    """ A hand-made simulation of gprMax output."""

    # set up a temporary directory and a couple of temporary files within
    tempdir = tmpdir_factory.mktemp('tempdir')
    basename = 'test_output'

    for i in range(4):
        file = tempdir / f'{basename}{i + 1}.out'

        rx_coord = [(i + 1) * 0.2, 0.5, 0]
        src_coord = [(i + 1) * 0.2, 0.5, 0]

        _write_example_output_into(file, rx_coord, src_coord)

    return basename


def test_Ascan_loads_correctly(sigle_Ascan):
    """ Test loading of single A-scan files. """

    out = Output.load_Ascan(sigle_Ascan)

    assert np.alltrue(out.Ex == output_file_data['Ex'])
    assert np.alltrue(out.Hy == output_file_data['Hy'])

    assert out.title == output_file_attrs['Title']
    assert out.iterations == output_file_attrs['Iterations']
    assert out.dt == output_file_attrs['dt']
    assert np.alltrue(out.dx_dy_dz == output_file_attrs['dx_dy_dz'])
    assert out.gprMax == output_file_attrs['gprMax']
    assert np.alltrue(out.nx_ny_nz == output_file_attrs['nx_ny_nz'])
    assert out.nrx == output_file_attrs['nrx']
    assert out.nsrc == output_file_attrs['nsrc']

    assert np.alltrue(out.t == np.arange(100) * 1e-12)

    assert out.rx_name == 'Rx(50,50,0)'
    assert np.alltrue(out.rx_position == [0.5, 0.5, 0])
    assert np.alltrue(out.src_position == [0.5, 0.5, 0])
    assert out.src_type == 'HertzianDipole'


@pytest.mark.skip(reason='WIP')
def test_Bscan_gathers_correctly(basename_of_series_of_Ascans):
    """ Test that series of A-scans gathers into a B-scan correctly. """

    out = Output.gather_Ascans(basename_of_series_of_Ascans)

    assert out.title == output_file_attrs['Title']
    assert out.iterations == output_file_attrs['Iterations']
    assert out.dt == output_file_attrs['dt']
    assert np.alltrue(out.dx_dy_dz == output_file_attrs['dx_dy_dz'])
    assert out.gprMax == output_file_attrs['gprMax']
    assert np.alltrue(out.nx_ny_nz == output_file_attrs['nx_ny_nz'])

    assert out.Ex.shape == out.Hy.shape == (out.traces, out.iterations)
    assert out.Ex[0, 0] == 1
    assert out.Hy[0, 0] == 5

    assert out.rx_names == [f'Rx({i * 20},50,0)' for i in range(1, 5)]
    assert out.rx_positions == [np.array([i * 0.2, 0.5, 0]) for i in range(1, 5)]
    assert out.src_positions == [np.array([i * 0.2, 0.5, 0]) for i in range(1, 5)]
    assert out.types == ['HertzianDipole' for i in range(1, 5)]


def _write_example_output_into(file, rx_coord, src_coord):
    """ This function writes an example hdf5 output into the specified file. """

    with h5py.File(file, 'w') as f:
        # create the root attributes using the dictionary above
        for key, value in output_file_attrs.items():
            f.attrs.create(key, value)

        # create the groups for receivers and sources
        rx1 = f.create_group('rxs/rx1')
        src1 = f.create_group('srcs/src1')

        # manually assign attributes to rx1 and src1 groups
        rx_coord_cells = (np.array(rx_coord) / output_file_attrs['dx_dy_dz']).astype(int)
        rx_name = 'Rx({},{},{})'.format(*rx_coord_cells)
        rx1.attrs.create('Name', rx_name)
        rx1.attrs.create('Position', rx_coord)

        src1.attrs.create('Position', src_coord)
        src1.attrs.create('Type', 'HertzianDipole')

        # create the datasets from the dictionary above
        for key, value in output_file_data.items():
            rx1.create_dataset(key, data=value)
