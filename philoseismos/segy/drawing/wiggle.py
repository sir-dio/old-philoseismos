import numpy as np


def wiggle_matrix(ax, matrix, dt, normalize):
    """ """

    time = np.linspace(0, matrix.shape[1] * dt, matrix.shape[1])

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

    ax.set_xlim(-0.75, matrix.shape[0] + 0.75)
    ax.set_ylim(time[-1], 0)
    ax.set_xlabel('Traces')
    ax.set_ylabel('Time [ms]')
