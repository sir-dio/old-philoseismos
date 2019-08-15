philoseismos: Documentation
========================================

.. module:: philoseismos

*philoseismos* is meant to be a toolbox for engineering seismologists.
This is sort of my passion project, driven by lots of annoying little
inefficiencies in the software I have to use working with near-surface
seismic surveys. The urge to find better tools aligns nicely with my love of
programming, and *philoseismos* is the the offspring of these two forces.

.. toctree::
    :maxdepth: 1
    :caption: Contents

    segy/segy
    coordinates/coordinates

.. code-block:: python
    :linenos:

    from philoseismos import Segy
    t = Segy('pr01_p001.sgy')

