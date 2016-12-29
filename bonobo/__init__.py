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

assert (sys.version_info >= (3, 5)), 'Python 3.5+ is required to use Bonobo.'

from ._version import __version__
from .core import *
from .io import CsvReader, CsvWriter, FileReader, FileWriter, JsonReader, JsonWriter
from .util import *

__all__ = [
    'Bag',
    'CsvReader',
    'CsvWriter',
    'FileReader',
    'FileWriter',
    'Graph',
    'JsonReader',
    'JsonWriter',
    'NOT_MODIFIED',
    'NaiveStrategy',
    'ProcessPoolExecutorStrategy',
    'ThreadPoolExecutorStrategy',
    '__version__',
    'console_run',
    'head',
    'inject',
    'jupyter_run',
    'log',
    'noop',
    'run',
    'service',
    'tee',
]
