from bonobo.structs import Bag, Graph, Token
from bonobo.nodes import CsvReader, CsvWriter, FileReader, FileWriter, Filter, JsonReader, JsonWriter, Limit, \
    PrettyPrinter, PickleWriter, PickleReader, Tee, count, identity, noop, pprint
from bonobo.strategies import create_strategy
from bonobo.util.objects import get_name

__all__ = []


def register_api(x, __all__=__all__):
    __all__.append(get_name(x))
    return x


def register_api_group(*args):
    for attr in args:
        register_api(attr)


@register_api
def run(graph, strategy=None, plugins=None, services=None):
    """
    Main entry point of bonobo. It takes a graph and creates all the necessary plumbery around to execute it.
    
    The only necessary argument is a :class:`Graph` instance, containing the logic you actually want to execute.
    
    By default, this graph will be executed using the "threadpool" strategy: each graph node will be wrapped in a
    thread, and executed in a loop until there is no more input to this node.
    
    You can provide plugins factory objects in the plugins list, this function will add the necessary plugins for
    interactive console execution and jupyter notebook execution if it detects correctly that it runs in this context.
    
    You'll probably want to provide a services dictionary mapping service names to service instances.
    
    :param Graph graph: The :class:`Graph` to execute.
    :param str strategy: The :class:`bonobo.strategies.base.Strategy` to use.
    :param list plugins: The list of plugins to enhance execution.
    :param dict services: The implementations of services this graph will use.
    :return bonobo.execution.graph.GraphExecutionContext:
    """
    strategy = create_strategy(strategy)

    plugins = plugins or []

    from bonobo import settings
    settings.check()

    if not settings.QUIET:  # pragma: no cover
        if _is_interactive_console():
            from bonobo.ext.console import ConsoleOutputPlugin
            if ConsoleOutputPlugin not in plugins:
                plugins.append(ConsoleOutputPlugin)

        if _is_jupyter_notebook():
            from bonobo.ext.jupyter import JupyterOutputPlugin
            if JupyterOutputPlugin not in plugins:
                plugins.append(JupyterOutputPlugin)

    return strategy.execute(graph, plugins=plugins, services=services)


# bonobo.structs
register_api_group(Bag, Graph, Token)

# bonobo.strategies
register_api(create_strategy)


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
    from os.path import expanduser

    return _open_fs(expanduser(str(fs_url)), *args, **kwargs)


# bonobo.nodes
register_api_group(
    CsvReader,
    CsvWriter,
    FileReader,
    FileWriter,
    Filter,
    JsonReader,
    JsonWriter,
    Limit,
    PrettyPrinter,
    PickleReader,
    PickleWriter,
    Tee,
    count,
    identity,
    noop,
    pprint,
)


def _is_interactive_console():
    import sys
    return sys.stdout.isatty()


def _is_jupyter_notebook():
    try:
        return get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        return False


@register_api
def get_examples_path(*pathsegments):
    import os
    import pathlib
    return str(pathlib.Path(os.path.dirname(__file__), 'examples', *pathsegments))


@register_api
def open_examples_fs(*pathsegments):
    return open_fs(get_examples_path(*pathsegments))
