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

## packages
The only package in the library so far is the **`Segy`** package.  
It introduces the **`Segy`** class that allows reading the most popular land seismic data format - **SEG-Y**.

## Segy
One of the main things **_philoseismos_** library offers is the **`Segy`** class,
that allows reading seismic data in the SEG-Y format.
```python
from philoseismos import Segy

t = Segy('a_segy_to_read.sgy')
```
A **`Segy`** object consists of three main parts, which corresponding to an element of the **SEG-Y** format
*(defined in [this document][1])*:
* **Textual File Header** object (`t.TFH`), that is meant to provide a human-readable description of the
seismic data in the file. The `t.TFH` object contains this description in the text form and allows reading and modifying it.
* **Binary File Header** object (`t.BFH`), that contains binary values relevant to the whole file,
like *sample format* and *trace length*.
* **Data** object (`t.Data`), that contains all the traces and trace headers in the file.

A full description of the class and its functionality will be provided in the docs _(now are in the process of being written)_.

[1]: https://seg.org/Portals/0/SEG/News%20and%20Resources/Technical%20Standards/seg_y_rev2_0-mar2017.pdf "SEG-Y revision 2.0 Data Exchange format"
