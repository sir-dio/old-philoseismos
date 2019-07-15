[![](https://img.shields.io/pypi/v/philoseismos.svg)](https://pypi.org/project/philoseismos/) [![](https://img.shields.io/pypi/pyversions/philoseismos.svg)](https://pypi.org/project/philoseismos/) [![](https://img.shields.io/pypi/l/philoseismos.svg)](https://pypi.org/project/philoseismos/) [![](https://img.shields.io/pypi/format/philoseismos.svg)](https://pypi.org/project/philoseismos/)

# *philoseismos*

<p align="center">
  <i>
    The Classical Greeks had a love for wisdom —  <br>
    It came down to us as <b>philo·sophia</b>.  <br>
    And I have a passion for the seismic method —  <br>
    Let this be an ode to <b>philo·seismos</b>.  <br>
    O how sweet it is —  <br>
    Listening to the echos from the earth. <br>
  </i>
</p>
<p align="right">
  <font size="-3"> Öz Yilmaz <br>
    Seismic Data Analysis </font>
</p>

*philoseismos is a toolbox library for a near-surface seismologists.*

## Working with .sgy files
One of the most important parts of the philoseismos library is a segy package
that defines a `Segy` class representing a .sgy file. It separates the files into its
main components: Textual file header, Binary file header, Data matrix (contains the traces in
numpy matrix form) and Geometry (contains the trace headers in pandas DataFrame form).

Loading a Segy file is as simple as it gets:
```python
from philoseismos import Segy

a = Segy('PR0001_P0001_R0001.sgy')
```

## Working with .wpt files
The philoseismos.coordinates package defines another useful class: `WayPoints`,
that represents a .wpt file used in OziExplorer.
