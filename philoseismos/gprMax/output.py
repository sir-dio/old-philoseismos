""" philoseismos: with passion for the seismic method.

This file defines the gprMax.Output class, used to load the output of gprMax.

@author: Dubrovin Ivan
e-mail: dubrovin.io@icloud.com """

import h5py
import numpy as np
import glob

from philoseismos.gprMax.constants import output_attributes


class Output:
    """ This object represents a gprMax output file. """

    def __init__(self):
        pass

    @classmethod
    def load_Ascan(cls, file):
        """ Create a new gprMax.Output object by loading a single A-scan output file. """

        new = cls()

        with h5py.File(file, 'r') as f:
            new.title = f.attrs['Title']
            new.iterations = f.attrs['Iterations']
            new.dt = f.attrs['dt']
            new.dx_dy_dz = f.attrs['dx_dy_dz']
            new.gprMax = f.attrs['gprMax']
            new.nrx = f.attrs['nrx']
            new.nsrc = f.attrs['nsrc']
            new.nx_ny_nz = f.attrs['nx_ny_nz']
            new.rxsteps = f.attrs['rxsteps']
            new.srcsteps = f.attrs['srcsteps']

            new.Ex = np.array(f['rxs/rx1/Ex'])
            new.Ey = np.array(f['rxs/rx1/Ey'])
            new.Ez = np.array(f['rxs/rx1/Ez'])
            new.Hx = np.array(f['rxs/rx1/Hx'])
            new.Hy = np.array(f['rxs/rx1/Hy'])
            new.Hz = np.array(f['rxs/rx1/Hz'])

            new.rx_name = f['rxs/rx1'].attrs['Name']
            new.rx_position = f['rxs/rx1'].attrs['Position']
            new.src_position = f['srcs/src1'].attrs['Position']
            new.src_type = f['srcs/src1'].attrs['Type']

        new.t = np.arange(new.iterations) * new.dt

        return new

    @classmethod
    def gather_Ascans(cls, basename):
        """ Create a B-scan by loading all the A-scans with a given basename. """

        new = cls()

        # find all the matching A-scans
        files = glob.glob(f'{basename}*.out')
        files.sort(key=lambda s: int(s[len(basename):-4]))

        new.traces = len(files)

        # create the lists to store rx names and positions, src positions and types
        new.rx_names = []
        new.rx_positions = []
        new.src_positions = []
        new.src_types = []

        # open the first one to load the attributes
        with h5py.File(files[0], 'r') as f:
            new.title = f.attrs['Title']
            new.iterations = f.attrs['Iterations']
            new.dt = f.attrs['dt']
            new.dx_dy_dz = f.attrs['dx_dy_dz']
            new.gprMax = f.attrs['gprMax']
            new.nx_ny_nz = f.attrs['nx_ny_nz']

            # save the first receiver and source attributes
            name, position = f['rxs/rx1'].attrs.values()
            new.rx_names.append(name)
            new.rx_positions.append(position)

            position, type = f['srcs/src1'].attrs.values()
            new.src_positions.append(position)
            new.src_types.append(type)

            # create the arrays to store the data
            new.Ex = np.empty(shape=(new.traces, new.iterations), dtype=np.float32)
            new.Ey = np.empty(shape=(new.traces, new.iterations), dtype=np.float32)
            new.Ez = np.empty(shape=(new.traces, new.iterations), dtype=np.float32)
            new.Hx = np.empty(shape=(new.traces, new.iterations), dtype=np.float32)
            new.Hy = np.empty(shape=(new.traces, new.iterations), dtype=np.float32)
            new.Hz = np.empty(shape=(new.traces, new.iterations), dtype=np.float32)

            # save the first trace
            new.Ex[0] = f['rxs/rx1/Ex']
            new.Ey[0] = f['rxs/rx1/Ey']
            new.Ez[0] = f['rxs/rx1/Ez']
            new.Hx[0] = f['rxs/rx1/Hx']
            new.Hy[0] = f['rxs/rx1/Hy']
            new.Hz[0] = f['rxs/rx1/Hz']

        # iterate through other files and load the remaining traces
        for i, file in enumerate(files[1:], 1):
            with h5py.File(file, 'r') as f:
                name, position = f['rxs/rx1'].attrs.values()
                new.rx_names.append(name)
                new.rx_positions.append(position)

                position, type = f['srcs/src1'].attrs.values()
                new.src_positions.append(position)
                new.src_types.append(type)

                new.Ex[i] = f['rxs/rx1/Ex']
                new.Ey[i] = f['rxs/rx1/Ey']
                new.Ez[i] = f['rxs/rx1/Ez']
                new.Hx[i] = f['rxs/rx1/Hx']
                new.Hy[i] = f['rxs/rx1/Hy']
                new.Hz[i] = f['rxs/rx1/Hz']

        new.t = np.arange(new.iterations) * new.dt

        return new
