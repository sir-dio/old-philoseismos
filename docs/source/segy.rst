SEG-Y files
===========

One of the packages in :code:`philoseismos` is called :code:`segy`, which introduces a :code:`Segy` object.

Structure of a :code:`Segy` object
----------------------------------

All the components of a SEG-Y file are represented by a corresponding object from the :code:`segy.components` package.
There are 4 components:

- **Textual File Header**. It's represented by a :code:`TextualFileHeader` object. Contains 3200 characters of text
  that describes the file.
- **Binary File Header**. It's represented by a :code:`BinaryFileHeader` object. Contains values relevant to
  the whole file, like sample format, number of traces, and sample interval.
- **Data traces**. Consists of trace headers and trace data. Represented by 2 separate objects:

  + :code:`Geometry` object - a table of all the trace header values.
  + :code:`DataMatrix` object - a matrix with trace data.

When a :code:`Segy` object is created, all these components are created automatically. To access them from a :code:`Segy`
instance, use corresponding attributes:

- :code:`.TFH` -- the textual file header.
- :code:`.BFH` -- the binary file header
- :code:`.G` -- the geometry table.
- :code:`.DM` -- the data matrix.

Example Usage
-------------------

The examples below assume that the the following import was made in advance:

.. code-block:: python

    from philoseismos import Segy

Loading SEG-Y files
...................

Loading SEG-Y files is as simple as initiating a new instance of a :code:`Segy` object with a path
to the file:

.. code-block:: python

    f = Segy('some_segy_file.sgy')

Another way is to create a new instance of a :code:`Segy` object without any arguments,
and instead use the :code:`.load_file()` method:

.. code-block:: python

    f = Segy()
    f.load_file('some_segy_file.sgy', progress=True)

