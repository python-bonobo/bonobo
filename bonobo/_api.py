from bonobo._version import __version__

__all__ = [
    '__version__',
]

from bonobo.structs import Bag, Graph

__all__ += ['Bag', 'Graph']

# Filesystem. This is a shortcut from the excellent filesystem2 library, that we make available there for convenience.
from fs import open_fs as _open_fs
open_fs = lambda url, *args, **kwargs: _open_fs(str(url), *args, **kwargs)
__all__ += ['open_fs']

# Basic transformations.
from bonobo.basics import *
from bonobo.basics import __all__ as _all_basics

__all__ += _all_basics

# Execution strategies.
from bonobo.strategies import create_strategy

__all__ += ['create_strategy']

# Extract and loads from stdlib.
from bonobo.io import *
from bonobo.io import __all__ as _all_io

__all__ += _all_io


# XXX This may be belonging to the bonobo.examples package.
def get_examples_path(*pathsegments):
    import os
    import pathlib
    return str(pathlib.Path(os.path.dirname(__file__), 'examples', *pathsegments))


__all__.append(get_examples_path.__name__)


def _is_interactive_console():
    import sys
    return sys.stdout.isatty()


def _is_jupyter_notebook():
    try:
        return get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        return False


# @api
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


__all__.append(run.__name__)
