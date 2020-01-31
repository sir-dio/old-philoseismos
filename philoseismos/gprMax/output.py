""" philoseismos: with passion for the seismic method.

This file defines the gprMax.Output class, used to load the output of gprMax.

@author: Dubrovin Ivan
e-mail: dubrovin.io@icloud.com """

import h5py
import numpy as np

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

        new.t = np.arange(new.iterations) * new.dt

        return new
