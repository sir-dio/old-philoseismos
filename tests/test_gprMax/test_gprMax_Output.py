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
def output_file(tmpdir_factory):
    """ A hand-made simulation of gprMax output. """

    # set up a temporary directory and a temporary file within
    tempdir = tmpdir_factory.mktemp('tempdir')
    file = tempdir / 'gprMax.out'

    # write the hand-made output to the temporary file
    with h5py.File(file, 'w') as f:
        # create the root attributes using the dictionary above
        for key, value in output_file_attrs.items():
            f.attrs.create(key, value)

        # create the groups for receivers and sources
        rx1 = f.create_group('rxs/rx1')
        src1 = f.create_group('srcs/src1')

        # manually assign attributes to rx1 and src1 groups
        rx1.attrs.create('Name', 'Rx(50,50,0)')
        rx1.attrs.create('Position', [0.5, 0.5, 0])

        src1.attrs.create('Position', [0.5, 0.5, 0])
        src1.attrs.create('Type', 'HertzianDipole')

        # create the datasets from the dictionary above
        for key, value in output_file_data.items():
            rx1.create_dataset(key, data=value)

    return file


def test_Ascan_loads_correctly(output_file):
    """ Test loading of single A-scan files. """

    out = Output.load_Ascan(output_file)

    assert np.alltrue(out.Ex == output_file_data['Ex'])
    assert np.alltrue(out.Hy == output_file_data['Hy'])
    assert out.title == output_file_attrs['Title']
    assert out.nsrc == output_file_attrs['nsrc']

    assert np.alltrue(out.t == np.arange(100) * 1e-12)
