import os

DEFAULT_SERVICES_FILENAME = '_services.py'
DEFAULT_SERVICES_ATTR = 'get_services'

DEFAULT_GRAPH_FILENAMES = ('__main__.py', 'main.py', )
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


def execute(filename, module, install=False, quiet=False, verbose=False):
    import runpy
    from bonobo import Graph, run, settings

    if quiet:
        settings.QUIET = True

    if verbose:
        settings.DEBUG = True

    if filename:
        if os.path.isdir(filename):
            if install:
                import importlib
                import pip
                requirements = os.path.join(filename, 'requirements.txt')
                pip.main(['install', '-r', requirements])
                # Some shenanigans to be sure everything is importable after this, especially .egg-link files which
                # are referenced in *.pth files and apparently loaded by site.py at some magic bootstrap moment of the
                # python interpreter.
                pip.utils.pkg_resources = importlib.reload(pip.utils.pkg_resources)
                import site
                importlib.reload(site)

            pathname = filename
            for filename in DEFAULT_GRAPH_FILENAMES:
                filename = os.path.join(pathname, filename)
                if os.path.exists(filename):
                    break
            if not os.path.exists(filename):
                raise IOError('Could not find entrypoint (candidates: {}).'.format(', '.join(DEFAULT_GRAPH_FILENAMES)))
        elif install:
            raise RuntimeError('Cannot --install on a file (only available for dirs containing requirements.txt).')
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

    # todo if console and not quiet, then add the console plugin
    # todo when better console plugin, add it if console and just disable display
    return run(
        graph,
        plugins=[],
        services=get_default_services(
            filename, context.get(DEFAULT_SERVICES_ATTR)() if DEFAULT_SERVICES_ATTR in context else None
        )
    )


def register_generic_run_arguments(parser, required=True):
    source_group = parser.add_mutually_exclusive_group(required=required)
    source_group.add_argument('filename', nargs='?', type=str)
    source_group.add_argument('--module', '-m', type=str)
    return parser


def register(parser):
    parser = register_generic_run_arguments(parser)
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('--quiet', '-q', action='store_true')
    verbosity_group.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--install', '-I', action='store_true')
    return execute
