""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import numpy as np


def imshow_matrix(ax, matrix, dt, normalize):
    """ Displays the data of the given matrix in form of
    the image using the matplotlib's imshow() method.

    Parameters
    ----------
    ax : matplotlib axes
        An axis object to display the image on.
    matrix : numpy 2D array
        A 2D numpy array where each row represents a trace.
    dt : int or float
        The sample interval in microseconds. Used to calculate
        the time axis for the traces.
    normalize : bool
        Enable / disable the normalization of each trace.
        Enabled by default.

    """

    data = matrix.T

    if normalize:
        max_ = np.abs(data).max(axis=0)
        max_[max_ == 0] = 1
        data = data / max_

    tmax = dt * matrix.shape[1] - dt
    ntraces = matrix.shape[0]
    ax.imshow(data, aspect='auto', cmap='binary', extent=[1, ntraces, tmax, 0])
