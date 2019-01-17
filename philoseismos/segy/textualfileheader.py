""" philoseismos: with passion for the seismic method.

@author: sir-dio
e-mail: dubrovin.io@icloud.com """


class TextualFileHeader:

    """ """

    def __init__(self, segy):
        """ """

        # store a reference to the Segy object:
        self._segy = segy

        # on initialization the TFH is empty:
        self._whole = ' ' * 3200

    def print(self, lines=True):
        """ """

        if lines:
            for i in range(40):
                print(f'{i + 1}. {self._get_line(i)}')
        else:
            for i in range(40):
                print(f'{self._get_line(i)}')

    def empty(self):
        """ """

        # replace _whole with spaces:
        self._whole = ' ' * 3200

    def change_line(self, line_no, text):
        """ """

        # crop and pad text to 80 symbols
        text = text.ljust(80)[:80]

        # calculate start and end of the line
        i1 = (line_no - 1) * 80
        i2 = line_no * 80

        # replace the line with text:
        self._whole = self._whole[:i1] + text + self._whole[i2:]

    # ========================== #
    # ===== Dunder methods ===== #

    def __repr__(self):
        s = 'Textual File Header object'
        return s if not self._whole.isspace() else f'{s} [empty]'

    def __str__(self):
        s = 'Textual File Header is empty.'
        return self._whole if not self._whole.isspace() else s

    # ============================ #
    # ===== Internal methods ===== #

    def _unpack_from_bytearray(self, bytearray_):
        """ """

        # check if the bytearray is of correct size:
        if len(bytearray_) != 3200:
            raise ValueError('TFH length does not equal 3200')

        self._whole = bytearray_.decode('cp500')
        self._whole = self._whole.replace('\x00', ' ')

    def _get_line(self, i):
        """ """

        return self._whole[i * 80: (i + 1) * 80]
