import argparse
import bonobo


def execute(file, quiet=False):
    with file:
        code = compile(file.read(), file.name, 'exec')

    # TODO: A few special variables should be set before running the file:
    #
    # See:
    #  - https://docs.python.org/3/reference/import.html#import-mod-attrs
    #  - https://docs.python.org/3/library/runpy.html#runpy.run_module
    context = {
        '__name__': '__bonobo__',
        '__file__': file.name,
    }

    try:
        exec(code, context)
    except Exception as exc:
        raise

    graphs = dict((k, v) for k, v in context.items() if isinstance(v, bonobo.Graph))

    assert len(graphs) == 1, (
        'Having zero or more than one graph definition in one file is unsupported for now, '
        'but it is something that will be implemented in the future.\n\nExpected: 1, got: {}.'
    ).format(len(graphs))

    name, graph = list(graphs.items())[0]

    # todo if console and not quiet, then add the console plugin
    # todo when better console plugin, add it if console and just disable display

    return bonobo.run(graph)


def register(parser):
    parser.add_argument('file', type=argparse.FileType())
    parser.add_argument('--quiet', action='store_true')
    return execute
