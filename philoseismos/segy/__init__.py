""" philoseismos: with passion for the seismic method.

@author: Ivan Dubrovin
e-mail: dubrovin.io@icloud.com """

# other modules
from philoseismos.segy.tools import general_functions as gfunc

# constants
from philoseismos.segy.tools.constants import BFH_columns

# SEG-Y components
from philoseismos.segy.components import TextualFileHeader
from philoseismos.segy.components import BinaryFileHeader
from philoseismos.segy.components import DataMatrix
from philoseismos.segy.components import Geometry
from philoseismos.segy.components import Segy
