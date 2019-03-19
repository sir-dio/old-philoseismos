""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import numpy as np
import pandas as pd
from tqdm import tqdm

from philoseismos.segy.tools.constants import sample_format_codes as sfc
from philoseismos.segy.tools.constants import trace_header_columns
from philoseismos.segy.tools.constants import data_type_map1, data_type_map2
from philoseismos.segy.trace import Trace


class Data:

    """ """

    def __init__(self, segy):
        """ """

        # store a reference to the Segy object:
        self._segy = segy

        # initialize a list of Traces:
        self.Traces = []

    def sort_traces(self):
        pass

    def delete_traces(self):
        pass

    def add_traces(self):
        pass

    # ============================ #
    # ===== Internal methods ===== #

    def _unpack_from_byteSegy(self):
        """ """

        sample_format = self._segy.BFH['Sample Format']

        # get sample size in bytes and format string for unpacking
        # from the mapping dictionary in constants.py
        self.sample_size, self._format_letter, _ = sfc[sample_format]

        # calculate trace length in bytes:
        trace_length = self._segy.BFH['Samples / Trace']
        self.trace_size_B = trace_length * self.sample_size

        # calculate the number of traces [240 is the size of a trace header]:
        self.num_traces = len(self._segy._byteSegy.data)
        self.num_traces /= (self.trace_size_B + 240)
        self.num_traces = int(self.num_traces)

        # define the shape for the DataMatrix
        DM_shape = (self.num_traces, trace_length)

        # create the geometry table:
        self.geometry = pd.DataFrame(index=range(1, self.num_traces + 1),
                                     columns=trace_header_columns)

        # create a DataMatrix with corresponding data type:
        self.DM = np.empty(DM_shape, dtype=data_type_map1[sample_format])

        # reset the Traces list in case it was not empty:
        self.Traces = []

        # unpack the traces:
        if self._segy.silent or self._segy._byteSegy.sizeMB < 5:
            for N in range(self.num_traces):
                trace = Trace(data=self, id_=N)
                trace._unpack_from_byteSegy()
                self.Traces.append(trace)
        else:
            # create a progress bar for files > 5 Mb:
            for N in tqdm(iterable=range(self.num_traces),
                          desc='Unpacking traces', unit=' traces',
                          postfix=f'file={self._segy.file.split("/")[-1]}'):
                trace = Trace(data=self, id_=N)
                trace._unpack_from_byteSegy()
                self.Traces.append(trace)

    def _import_DataMatrix(self, DM):
        """ """

        # save the DataMatrix itself:
        self.DM = DM

        # restore the parameters from the DM
        self.num_traces = DM.shape[0]
        sample_format = data_type_map2[DM.dtype]
        self.sample_size, self._format_letter, _ = sfc[sample_format]

        # reset the Traces list:
        self.Traces = []

        # create the geometry table:
        self.geometry = pd.DataFrame(index=range(1, self.num_traces + 1),
                                     columns=trace_header_columns)
        self.geometry.fillna(0, inplace=True)

        # iterate over DM creating Traces:
        for N in range(self.num_traces):
            self.Traces.append(Trace(data=self, id_=N))
            self.Traces[N]._get_values_from_DataMatrix()

    # =================================== #
    # ===== Internal helper methods ===== #
