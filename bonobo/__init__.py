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
import warnings

assert (sys.version_info >= (3, 5)), 'Python 3.5+ is required to use Bonobo.'

from ._version import __version__
from .config import *
from .context import *
from .core import *
from .io import *
from .util import *

DEFAULT_STRATEGY = 'threadpool'

STRATEGIES = {
    'naive': NaiveStrategy,
    'processpool': ProcessPoolExecutorStrategy,
    'threadpool': ThreadPoolExecutorStrategy,
}


def run(graph, *chain, strategy=None, plugins=None):
    from bonobo.core.strategies.base import Strategy

    if len(chain):
        warnings.warn('DEPRECATED. You should pass a Graph instance instead of a chain.')
        from bonobo import Graph
        graph = Graph(graph, *chain)

    if not isinstance(strategy, Strategy):
        if strategy is None:
            strategy = DEFAULT_STRATEGY

        try:
            strategy = STRATEGIES[strategy]
        except KeyError as exc:
            raise RuntimeError('Invalid strategy {}.'.format(repr(strategy))) from exc

        strategy = strategy()

    return strategy.execute(graph, plugins=plugins)


__all__ = [
    'Bag',
    'Configurable',
    'ContextProcessor',
    'contextual',
    'CsvReader',
    'CsvWriter',
    'FileReader',
    'FileWriter',
    'Graph',
    'JsonReader',
    'JsonWriter',
    'NOT_MODIFIED',
    'NaiveStrategy',
    'Option',
    'ProcessPoolExecutorStrategy',
    'ThreadPoolExecutorStrategy',
    '__version__',
    'console_run',
    'inject',
    'jupyter_run',
    'limit',
    'log',
    'noop',
    'pprint',
    'service',
    'tee',
]

del warnings
del sys
