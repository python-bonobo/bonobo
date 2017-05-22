import os
import runpy

import bonobo

DEFAULT_SERVICES_FILENAME = '_services.py'
DEFAULT_SERVICES_ATTR = 'get_services'

DEFAULT_GRAPH_FILENAME = '__main__.py'
DEFAULT_GRAPH_ATTR = 'get_graph'


def get_default_services(filename, services=None):
    dirname = os.path.dirname(filename)
    services_filename = os.path.join(dirname, DEFAULT_SERVICES_FILENAME)
    if os.path.exists(services_filename):
        with open(services_filename) as file:
            code = compile(file.read(), services_filename, 'exec')
        context = {
            '__name__': '__bonobo__',
            '__file__': services_filename,
        }
        try:
            exec(code, context)
        except Exception:
            raise
        return {
            **context[DEFAULT_SERVICES_ATTR](),
            **(services or {}),
        }
    return services or {}


def execute(filename, module, quiet=False, verbose=False):
    from bonobo import settings

    if quiet:
        settings.QUIET = True

    if verbose:
        settings.DEBUG = True

    if filename:
        if os.path.isdir(filename):
            filename = os.path.join(filename, DEFAULT_GRAPH_FILENAME)
        context = runpy.run_path(filename, run_name='__bonobo__')
    elif module:
        context = runpy.run_module(module, run_name='__bonobo__')
        filename = context['__file__']
    else:
        raise RuntimeError('UNEXPECTED: argparse should not allow this.')

    graphs = dict((k, v) for k, v in context.items() if isinstance(v, bonobo.Graph))

    assert len(graphs) == 1, (
        'Having zero or more than one graph definition in one file is unsupported for now, '
        'but it is something that will be implemented in the future.\n\nExpected: 1, got: {}.'
    ).format(len(graphs))

    graph = list(graphs.values())[0]

    # todo if console and not quiet, then add the console plugin
    # todo when better console plugin, add it if console and just disable display
    return bonobo.run(
        graph,
        plugins=[],
        services=get_default_services(
            filename, context.get(DEFAULT_SERVICES_ATTR)() if DEFAULT_SERVICES_ATTR in context else None
        )
    )


def register(parser):
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('filename', nargs='?', type=str)
    source_group.add_argument('--module', '-m', type=str)
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('--quiet', '-q', action='store_true')
    verbosity_group.add_argument('--verbose', '-v', action='store_true')
    return execute
