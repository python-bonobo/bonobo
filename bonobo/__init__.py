import sys
from .core import *
from .io import *
from .util import *

PY35 = (sys.version_info >= (3, 5))

assert PY35, 'Python 3.5+ is required to use Bonobo.'

# Version infos
try:
    with open('../version.txt') as f:
        __version__ = f.read().strip()
except Exception as e:
    __version__ = 'dev'
