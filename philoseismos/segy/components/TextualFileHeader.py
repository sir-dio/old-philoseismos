""" philoseismos: with passion for the seismic method.

This file defines the TextualFileHeader object that represents
a Textual File Header of a SEG-Y file.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """


class TextualFileHeader:
    """ Textual File Header for the SEG-Y file.

     Textual description of the file. Exactly 3200 characters.
     40 lines, 80 characters each. No strict format.

     """

    def __init__(self):
        """ Create an empty Textual File Header object. """

        # standard encoding specified in SEG-Y file format description
        self.encoding = 'cp500'

        self.text = ' ' * 3200
        self.lines = [self.text[i * 80: (i + 1) * 80] for i in range(40)]

        self._bytes = None

    # ----- Loading, decoding, writing ----- #

    def load_from_file(self, file):
        """ Loads the bytes representing a Textual File Header.

        Arguments
            file (str)
                Path to the file to load the Textual File Header from.

        """

        with open(file, 'br') as f:
            bytes = f.read(3200)

        self.load_from_bytes(bytes)

    def replace_in_file(self, file):
        """ Replaces the Textual File Header in the file with self.

        Arguments
            file (str)
                Path to the file to replace Textual File Header in.

        """

        self._bytes = self.text.encode(self.encoding)

        with open(file, 'br') as f:
            file_content = bytearray(f.read())

        file_content[:3200] = self._bytes

        with open(file, 'bw') as f:
            f.write(file_content)

    def load_from_bytes(self, bytes):
        """ Unpacks given bytes into self.

        Arguments
            bytes (bytes)
                Bytes to decode.

        """

        self._bytes = bytes
        self.text = bytes.decode(self.encoding)
        self.lines = [self.text[i * 80: (i + 1) * 80] for i in range(40)]

    def redecode(self):
        """ Decodes bytes, loaded from file, using the endoding..

        Can be useful if the encoding was changed, to reset the .text attribute. """

        self.text = self._bytes.decode(self.encoding)

    # ----- Modifying content ----- #

    def set_content(self, content):
        """ Set the content for the Textual File Header.

        Arguments
            content (str)
                New content for the Textual File Header.

        Notes
            Textual File Header has to contain exactly 3200 characters: 40 lines, 80 symbols each.

            The given content is splitted into lines by a new line symbol. If there are more than 40,
            only the first 40 are taken. Each line is then set to be exactly 80 characters long.
            If there are less then 40 lines, empty lines are added.

        """

        lines = content.split('\n')[:40]
        self.lines = [line[:80].ljust(80) for line in lines]

        while len(self.lines) < 40:
            self.lines.append(' ' * 80)

        self.text = ''.join(self.lines)

        self._bytes = self.text.encode(self.encoding)

    def set_line(self, line_no, content):
        """ Set the content for a specific line.

        Arguments
            line_no (int)
                Number of the line to change (starting from 1).
            content (str)
                New content for the line.

        Notes
            Since each line in Textual File Header is exactly 80 characters, the content is cropped
            or padded with spaces.

        """

        line = content[:80].ljust(80)
        self.lines[line_no - 1] = line
        self.text = ''.join(self.lines)

        self._bytes = self.text.encode(self.encoding)

    # ----- Working with other files ----- #

    def export_to_txt(self, file):
        """ Saves the content of the Textual File Header in .txt format.

        Arguments
            file (str)
                Path and name of the file to export Textual File Header to.

        Notes
            Lines are separated.

        """

        with open(file, 'w') as f:
            for line in self.lines:
                f.write(line + '\n')

    def import_from_txt(self, file):
        """ Loads the content from the .txt file.

        Arguments
            file (str)
                Path to the file to import Textual File Header from.

        Notes
            Reads 40 lines, 80 characters each, and combines them.

        """

        with open(file, 'r') as f:
            self.lines = [f.readline().strip()[:80].ljust(80) for i in range(40)]

        self.text = ''.join(self.lines)

    # ----- Dunder methods ----- #

    def __repr__(self):
        return '\n'.join(self.lines)
