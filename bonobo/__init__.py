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
from .basics import __all__ as __all_basics__
from .config import __all__ as __all_config__
from .execution import __all__ as __all_execution__
from .io import __all__ as __all_io__
from .strategies import __all__ as __all_strategies__

__all__ = __all_basics__ + __all_config__ + __all_execution__ + __all_io__ + __all_strategies__ + [
    'Bag',
    'ErrorBag'
    'Graph',
    'Token',
    '__version__',
    'create_strategy',
    'get_examples_path',
    'run',
]

from .basics import *
from .config import *
from .execution import *
from .io import *
from .strategies import *
from .structs.bags import *
from .structs.graphs import *
from .structs.tokens import *

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
    """
    Create a strategy, or just returns it if it's already one.
    
    :param name: 
    :return: Strategy
    """
    from bonobo.strategies.base import Strategy
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


def _is_interactive_console():
    import sys
    return sys.stdout.isatty()


def _is_jupyter_notebook():
    try:
        return get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        return False


def run(graph, *chain, strategy=None, plugins=None, services=None):
    if len(chain):
        warnings.warn('DEPRECATED. You should pass a Graph instance instead of a chain.')
        from bonobo import Graph
        graph = Graph(graph, *chain)

    strategy = create_strategy(strategy)
    plugins = []

    if _is_interactive_console():
        from bonobo.ext.console import ConsoleOutputPlugin
        if ConsoleOutputPlugin not in plugins:
            plugins.append(ConsoleOutputPlugin)

    if _is_jupyter_notebook():
        from bonobo.ext.jupyter import JupyterOutputPlugin
        if JupyterOutputPlugin not in plugins:
            plugins.append(JupyterOutputPlugin)

    return strategy.execute(graph, plugins=plugins, services=services)


del sys
del warnings
