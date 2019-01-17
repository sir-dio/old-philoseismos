""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """

import numpy as np
import pandas as pd
from tqdm import tqdm

from philoseismos.segy.tools.constants import sample_format_codes as sfc
from philoseismos.segy.tools.constants import trace_header_list
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

    def _unpack_from_bytearray(self, bytearray_, sample_format, trace_length):
        """ """

        # get sample size in bytes and format string for unpacking
        # from the mapping dictionary in constants.py
        self.sample_size, self._format_letter, _ = sfc[sample_format]

        # calculate trace length in bytes:
        self.trace_size_B = trace_length * self.sample_size

        # calculate the number of traces [240 is the size of a trace header]:
        self.num_traces = int(len(bytearray_) / (self.trace_size_B + 240))

        # create a DataMatrix with corresponding data type:
        DM_shape = (self.num_traces, trace_length)

        if sample_format == 1:         # R4 IBM in RadexPro
            self.DM = np.empty(DM_shape, dtype=np.float32)
        elif sample_format == 2:       # I4 in RadexPro
            self.DM = np.empty(DM_shape, dtype=np.int32)
        elif sample_format == 3:       # I2 in RadexPro
            self.DM = np.empty(DM_shape, dtype=np.int16)
        elif sample_format == 5:       # R4 in RadexPro
            self.DM = np.empty(DM_shape, dtype=np.float32)
        elif sample_format == 6:
            self.DM = np.empty(DM_shape, dtype=np.float64)
        elif sample_format == 8:       # I1 in RadexPro
            self.DM = np.empty(DM_shape, dtype=np.int8)
        elif sample_format == 9:
            self.DM = np.empty(DM_shape, dtype=np.int64)
        elif sample_format == 10:
            self.DM = np.empty(DM_shape, dtype=np.uint32)
        elif sample_format == 11:
            self.DM = np.empty(DM_shape, dtype=np.uint16)

        # create a DataFrame for the geometry:
        self.geometry = pd.DataFrame(
            index=range(1, 1 + self.num_traces),
            columns=trace_header_list)

        # reset the Traces list in case it was not empty:
        self.Traces = []

        # iterate over data bytes unpacking traces:
        if self._segy.silent or self._segy._byteSegy.sizeMB < 5:
            # load with no progress bar:
            for N in range(self.num_traces):
                # extract the bytes for each individual trace:
                trace_bytes = self._get_trace_bytes(bytearray_, N)
                # add a new Trace object to the list of traces:
                self.Traces.append(Trace(data=self, id=N))
                # unpack a trace from bytes:
                self.Traces[N]._unpack_from_bytearray(trace_bytes,
                                                      sample_format,
                                                      trace_length)
                self.geometry.at[N + 1, '_trace'] = self.Traces[N]
        else:
            # create a progress bar for files > 5 Mb:
            for N in tqdm(iterable=range(self.num_traces),
                          desc='Unpacking traces', unit=' traces',
                          postfix=f'file={self._segy.file}'):

                trace_bytes = self._get_trace_bytes(bytearray_, N)
                self.Traces.append(Trace(data=self, id=N))
                self.Traces[N]._unpack_from_bytearray(trace_bytes,
                                                      sample_format,
                                                      trace_length)
                self.geometry.at[N + 1, '_trace'] = self.Traces[N]

    # =================================== #
    # ===== Internal helper methods ===== #

    def _get_unpacking_parameters_from_BFH(self, BFH):
        """ """

        table = BFH.table
        parameters = {
            'sample_format': table['Sample Format'],
            'trace_length': table['Samples / Trace']
        }
        return parameters

    def _get_trace_bytes(self, bytearray_, traceno):
        start_byte = (self.trace_size_B + 240) * traceno
        end_byte = (self.trace_size_B + 240) * (traceno + 1)
        return bytearray_[start_byte:end_byte]
