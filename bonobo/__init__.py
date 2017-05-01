# Bonobo data-processing toolkit.
#
# Bonobo is a line-by-line data-processing toolkit for python 3.5+ emphasizing simplicity and atomicity of data
# transformations using a simple directed graph of python callables.
#
# Licensed under Apache License 2.0, read the LICENSE file in the root of the source tree.
"""Bonobo data-processing toolkit main module."""

import sys

assert (sys.version_info >= (3, 5)), 'Python 3.5+ is required to use Bonobo.'
from bonobo._api import *
from bonobo._api import __all__
from bonobo._version import __version__

__all__ = ['__version__'] + __all__
__version__ = __version__

del sys
