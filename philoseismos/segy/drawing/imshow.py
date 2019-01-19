import numpy as np


def imshow_matrix(ax, matrix, dt, normalize):
    """ """

    data = matrix.T

    if normalize:
        max_ = np.abs(data).max(axis=0)
        max_[max_ == 0] = 1
        data = data / max_

    tmax = dt * matrix.shape[1] - dt
    ntraces = matrix.shape[0]
    ax.imshow(data, aspect='auto', cmap='binary', extent=[1, ntraces, tmax, 0])
