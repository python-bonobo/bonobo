""" Bonobo data-processing toolkit.

    Bonobo is a line-by-line data-processing toolkit for python 3.5+ emphasizing simplicity and atomicity of data
    transformations using a simple directed graph of python callables.

    Read more at http://docs.bonobo-project.org/

    Copyright 2012-2014 Romain Dorgueil

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

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
except Exception as exc:
    __version__ = 'dev'

__all__ = [
    'Bag',
    'Graph',
    'NaiveStrategy',
    'NotModified',
    'ProcessPoolExecutorStrategy',
    'ThreadPoolExecutorStrategy',
    'head',
    'inject',
    'log',
    'noop',
    'service',
    'tee',
    'to_json',
]
