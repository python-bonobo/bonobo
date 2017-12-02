from bonobo.execution.strategies import create_strategy
from bonobo.nodes import __all__ as _all_nodes
from bonobo.nodes import *
from bonobo.structs import Graph
from bonobo.util import get_name
from bonobo.util.environ import parse_args, get_argument_parser

__all__ = []


def register_api(x, __all__=__all__):
    """Register a function as being part of Bonobo's API, then returns the original function."""
    __all__.append(get_name(x))
    return x


def register_graph_api(x, __all__=__all__):
    """
    Register a function as being part of Bonobo's API, after checking that its signature contains the right parameters
    to work correctly, then returns the original function.
    """
    from inspect import signature
    parameters = list(signature(x).parameters)
    required_parameters = {'plugins', 'services', 'strategy'}
    assert parameters[0] == 'graph', 'First parameter of a graph api function must be "graph".'
    assert required_parameters.intersection(
        parameters
    ) == required_parameters, 'Graph api functions must define the following parameters: ' + ', '.join(
        sorted(required_parameters)
    )

    return register_api(x, __all__=__all__)


def register_api_group(*args, check=None):
    check = set(check) if check else None
    for attr in args:
        register_api(attr)
        if check:
            check.remove(get_name(attr))
    assert not (check and len(check))


@register_graph_api
def run(graph, *, plugins=None, services=None, strategy=None):
    """
    Main entry point of bonobo. It takes a graph and creates all the necessary plumbing around to execute it.

    The only necessary argument is a :class:`Graph` instance, containing the logic you actually want to execute.

    By default, this graph will be executed using the "threadpool" strategy: each graph node will be wrapped in a
    thread, and executed in a loop until there is no more input to this node.

    You can provide plugins factory objects in the plugins list, this function will add the necessary plugins for
    interactive console execution and jupyter notebook execution if it detects correctly that it runs in this context.

    You'll probably want to provide a services dictionary mapping service names to service instances.

    :param Graph graph: The :class:`Graph` to execute.
    :param str strategy: The :class:`bonobo.execution.strategies.base.Strategy` to use.
    :param list plugins: The list of plugins to enhance execution.
    :param dict services: The implementations of services this graph will use.
    :return bonobo.execution.graph.GraphExecutionContext:
    """

    plugins = plugins or []

    from bonobo import settings
    settings.check()

    if not settings.QUIET.get():  # pragma: no cover
        if _is_interactive_console():
            import mondrian
            mondrian.setup(excepthook=True)

            from bonobo.plugins.console import ConsoleOutputPlugin
            if ConsoleOutputPlugin not in plugins:
                plugins.append(ConsoleOutputPlugin)

        if _is_jupyter_notebook():
            try:
                from bonobo.contrib.jupyter import JupyterOutputPlugin
            except ImportError:
                import logging
                logging.warning(
                    'Failed to load jupyter widget. Easiest way is to install the optional "jupyter" '
                    'dependencies with «pip install bonobo[jupyter]», but you can also install a specific '
                    'version by yourself.'
                )
            else:
                if JupyterOutputPlugin not in plugins:
                    plugins.append(JupyterOutputPlugin)

    import logging
    logging.getLogger().setLevel(settings.LOGGING_LEVEL.get())
    strategy = create_strategy(strategy)
    return strategy.execute(graph, plugins=plugins, services=services)


def _inspect_as_graph(graph):
    return graph._repr_dot_()


_inspect_formats = {'graph': _inspect_as_graph}


@register_graph_api
def inspect(graph, *, plugins=None, services=None, strategy=None, format):
    if not format in _inspect_formats:
        raise NotImplementedError(
            'Output format {} not implemented. Choices are: {}.'.format(
                format, ', '.join(sorted(_inspect_formats.keys()))
            )
        )
    print(_inspect_formats[format](graph))


# data structures
register_api_group(Graph)

# execution strategies
register_api(create_strategy)


# Shortcut to filesystem2's open_fs, that we make available there for convenience.
@register_api
def open_fs(fs_url=None, *args, **kwargs):
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
    from os import getcwd

    if fs_url is None:
        fs_url = getcwd()

    return _open_fs(expanduser(str(fs_url)), *args, **kwargs)


# standard transformations
register_api_group(
    CsvReader,
    CsvWriter,
    FileReader,
    FileWriter,
    Filter,
    FixedWindow,
    Format,
    JsonReader,
    JsonWriter,
    LdjsonReader,
    LdjsonWriter,
    Limit,
    OrderFields,
    PickleReader,
    PickleWriter,
    PrettyPrinter,
    RateLimited,
    Rename,
    SetFields,
    Tee,
    UnpackItems,
    count,
    identity,
    noop,
    check=_all_nodes,
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


register_api_group(get_argument_parser, parse_args)
