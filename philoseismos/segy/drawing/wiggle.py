""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import numpy as np


def wiggle_matrix(ax, matrix, dt, normalize):
    """ Displays the data of the given matrix in form of
    the seismic wiggle trace image.

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

    # calculate the time axis:
    time = np.linspace(0, matrix.shape[1] * dt, matrix.shape[1])

    # iterate over each trace
    for i, tr in enumerate(matrix):
        j = i + 1

        if normalize and not np.all(tr == 0):
            trace = tr / np.abs(tr).max() * 0.5
        else:
            trace = tr

        ax.plot(trace + j, time, color='k')
        ax.fill_betweenx(time, trace + j, j,
                         where=((trace + j) >= j),
                         color='k')

    # set the limits for the axis:
    ax.set_xlim(-0.75, matrix.shape[0] + 0.75)
    ax.set_ylim(time[-1], 0)
    # set the axis labels:
    ax.set_xlabel('Traces')
    ax.set_ylabel('Time [ms]')
