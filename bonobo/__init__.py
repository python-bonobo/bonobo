# Bonobo data-processing toolkit.
#
# Bonobo is a line-by-line data-processing toolkit for python 3.5+ emphasizing simplicity and atomicity of data
# transformations using a simple directed graph of python callables.
#
# Licensed under Apache License 2.0, read the LICENSE file in the root of the source tree.
"""Bonobo data-processing toolkit main module."""

import sys
import warnings

assert (sys.version_info >= (3, 5)), 'Python 3.5+ is required to use Bonobo.'

from ._version import __version__
from .config import __all__ as __all_config__
from .context import __all__ as __all_context__
from .core import __all__ as __all_core__
from .io import __all__ as __all_io__
from .util import __all__ as __all_util__

__all__ = __all_config__ + __all_context__ + __all_core__ + __all_io__ + __all_util__ + [
    '__version__',
    'create_strategy',
    'get_examples_path',
    'run',
]

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


def get_examples_path(*pathsegments):
    import os
    import pathlib
    return str(pathlib.Path(os.path.dirname(__file__), 'examples', *pathsegments))


def create_strategy(name=None):
    from bonobo.core.strategies.base import Strategy
    import logging

    if isinstance(name, Strategy):
        return name

    if name is None:
        name = DEFAULT_STRATEGY

    logging.debug('Creating strategy {}...'.format(name))

    try:
        factory = STRATEGIES[name]
    except KeyError as exc:
        raise RuntimeError(
            'Invalid strategy {}. Available choices: {}.'.format(repr(name), ', '.join(sorted(STRATEGIES.keys())))
        ) from exc

    return factory()


def run(graph, *chain, strategy=None, plugins=None):
    strategy = create_strategy(strategy)

    if len(chain):
        warnings.warn('DEPRECATED. You should pass a Graph instance instead of a chain.')
        from bonobo import Graph
        graph = Graph(graph, *chain)

    return strategy.execute(graph, plugins=plugins)


del sys
del warnings
