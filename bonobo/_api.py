from bonobo.basics import Limit, PrettyPrint, Tee, count, identity, noop, pprint
from bonobo.strategies import create_strategy
from bonobo.structs import Bag, Graph
from bonobo.util.objects import get_name
from bonobo.io import CsvReader, CsvWriter, FileReader, FileWriter, JsonReader, JsonWriter

__all__ = []


def register_api(x, __all__=__all__):
    __all__.append(get_name(x))
    return x

def register_api_group(*args):
    for attr in args:
        register_api(attr)


# bonobo.basics
register_api_group(Limit, PrettyPrint, Tee, count, identity, noop, pprint, )

# bonobo.io
register_api_group(CsvReader, CsvWriter, FileReader, FileWriter, JsonReader, JsonWriter)

# bonobo.strategies
register_api(create_strategy)

# bonobo.structs
register_api_group(Bag, Graph)

# Shortcut to filesystem2's open_fs, that we make available there for convenience.
@register_api
def open_fs(fs_url, *args, **kwargs):
    """
    Wraps :func:`fs.open_fs` function with a few candies.
    
    :param str fs_url: A filesystem URL
    :param parse_result: A parsed filesystem URL.
    :type parse_result: :class:`ParseResult`
    :param bool writeable: True if the filesystem must be writeable.
    :param bool create: True if the filesystem should be created if it does not exist.
    :param str cwd: The current working directory (generally only relevant for OS filesystems).
    :param str default_protocol: The protocol to use if one is not supplied in the FS URL (defaults to ``"osfs"``).
    :returns: :class:`~fs.base.FS` object
    """
    from fs import open_fs as _open_fs
    return _open_fs(str(fs_url), *args, **kwargs)



def _is_interactive_console():
    import sys
    return sys.stdout.isatty()


def _is_jupyter_notebook():
    try:
        return get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        return False


@register_api
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


@register_api
def get_examples_path(*pathsegments):
    import os
    import pathlib
    return str(pathlib.Path(os.path.dirname(__file__), 'examples', *pathsegments))


@register_api
def open_examples_fs(*pathsegments):
    return open_fs(get_examples_path(*pathsegments))


print(__all__)
