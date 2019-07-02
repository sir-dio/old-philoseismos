""" philoseismos: with passion for the seismic method.

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
        """ Loads the bytes representing a Textual File Header. """

        with open(file, 'br') as f:
            bytes = f.read(3200)

        self.load_from_bytes(bytes)

    def replace_in_file(self, file):
        """ Replaces the Textual File Header in the file with self. """

        self._bytes = self.text.encode(self.encoding)

        with open(file, 'br') as f:
            file_content = bytearray(f.read())

        file_content[:3200] = self._bytes

        with open(file, 'bw') as f:
            f.write(file_content)

    def load_from_bytes(self, bytes):
        """ Unpacks given bytes into self. """

        self._bytes = bytes
        self.text = bytes.decode(self.encoding)
        self.lines = [self.text[i * 80: (i + 1) * 80] for i in range(40)]

    def redecode(self):
        """ Decodes bytes, loaded from file, using the endoding..

        Can be useful if the encoding was changed, to reset the .text attribute. """

        self.text = self._bytes.decode(self.encoding)

    # ----- Modifying content ----- #

    def set_content(self, content):
        """ Set the content for the Textual File Header. """

        # crop and pad the content
        self.text = content[:3200].ljust(3200)
        self.lines = [self.text[i * 80: (i + 1) * 80] for i in range(40)]

        self._bytes = self.text.encode(self.encoding)

    def set_line(self, line_no, content):
        """ Set the content for a specific line. """

        line = content[:80].ljust(80)
        self.lines[line_no - 1] = line
        self.text = ''.join(self.lines)

        self._bytes = self.text.encode(self.encoding)

    # ----- Working with other files ----- #

    def export_to_txt(self, file):
        """ Saves the content of the Textual File Header in .txt format.

        Lines are separated. """

        with open(file, 'w') as f:
            for line in self.lines:
                f.write(line + '\n')

    def import_from_txt(self, file):
        """ Loads the content from the .txt file.

        Reads 40 lines, 80 characters each, and combines them.

        """

        with open(file, 'r') as f:
            self.lines = [f.readline().strip()[:80].ljust(80) for i in range(40)]

        self.text = ''.join(self.lines)

    # ----- Dunder methods ----- #

    def __repr__(self):
        return '\n'.join(self.lines)
