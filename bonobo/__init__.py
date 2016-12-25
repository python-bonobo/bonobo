import sys
from .core import *
from .io import *
from .util import *

PY35 = (sys.version_info >= (3, 5))

assert PY35, 'Python 3.5+ is required to use Bonobo.'

__version__ = '0.0.0'
