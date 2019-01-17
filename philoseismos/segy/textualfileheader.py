""" philoseismos: with passion for the seismoc method.

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
