import os

import bonobo
from bonobo.constants import DEFAULT_SERVICES_ATTR, DEFAULT_SERVICES_FILENAME

DEFAULT_GRAPH_FILENAMES = (
    '__main__.py',
    'main.py',
)
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
        exec(code, context)

        return {
            **context[DEFAULT_SERVICES_ATTR](),
            **(services or {}),
        }
    return services or {}


def _install_requirements(requirements):
    """Install requirements given a path to requirements.txt file."""
    import importlib
    import pip

    pip.main(['install', '-r', requirements])
    # Some shenanigans to be sure everything is importable after this, especially .egg-link files which
    # are referenced in *.pth files and apparently loaded by site.py at some magic bootstrap moment of the
    # python interpreter.
    pip.utils.pkg_resources = importlib.reload(pip.utils.pkg_resources)
    import site
    importlib.reload(site)


def read(filename, module, install=False, quiet=False, verbose=False, env=None):
    import re
    import runpy
    from bonobo import Graph, settings

    if quiet:
        settings.QUIET.set(True)

    if verbose:
        settings.DEBUG.set(True)

    if env:
        quote_killer = re.compile('["\']')
        for e in env:
            var_name, var_value = e.split('=')
            os.environ[var_name] = quote_killer.sub('', var_value)

    if filename:
        if os.path.isdir(filename):
            if install:
                requirements = os.path.join(filename, 'requirements.txt')
                _install_requirements(requirements)

            pathname = filename
            for filename in DEFAULT_GRAPH_FILENAMES:
                filename = os.path.join(pathname, filename)
                if os.path.exists(filename):
                    break
            if not os.path.exists(filename):
                raise IOError('Could not find entrypoint (candidates: {}).'.format(', '.join(DEFAULT_GRAPH_FILENAMES)))
        elif install:
            requirements = os.path.join(os.path.dirname(filename), 'requirements.txt')
            _install_requirements(requirements)
        context = runpy.run_path(filename, run_name='__bonobo__')
    elif module:
        context = runpy.run_module(module, run_name='__bonobo__')
        filename = context['__file__']
    else:
        raise RuntimeError('UNEXPECTED: argparse should not allow this.')

    graphs = dict((k, v) for k, v in context.items() if isinstance(v, Graph))

    assert len(graphs) == 1, (
        'Having zero or more than one graph definition in one file is unsupported for now, '
        'but it is something that will be implemented in the future.\n\nExpected: 1, got: {}.'
    ).format(len(graphs))

    graph = list(graphs.values())[0]
    plugins = []
    services = get_default_services(
        filename, context.get(DEFAULT_SERVICES_ATTR)() if DEFAULT_SERVICES_ATTR in context else None
    )

    return graph, plugins, services


def execute(filename, module, install=False, quiet=False, verbose=False, env=None):
    graph, plugins, services = read(filename, module, install, quiet, verbose, env)

    return bonobo.run(graph, plugins=plugins, services=services)


def register_generic_run_arguments(parser, required=True):
    source_group = parser.add_mutually_exclusive_group(required=required)
    source_group.add_argument('filename', nargs='?', type=str)
    source_group.add_argument('--module', '-m', type=str)
    parser.add_argument('--env', '-e', action='append')
    return parser


def register(parser):
    parser = register_generic_run_arguments(parser)
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('--quiet', '-q', action='store_true')
    verbosity_group.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--install', '-I', action='store_true')
    return execute
