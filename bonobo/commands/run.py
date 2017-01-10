import argparse

from bonobo import Graph, console_run


def execute(file):
    with file:
        code = compile(file.read(), file.name, 'exec')

    context = {}

    try:
        exec(code, context)
    except Exception as exc:
        raise

    graphs = dict((k, v) for k, v in context.items() if isinstance(v, Graph))

    assert len(graphs) == 1, 'Having more than one graph definition in one file is unsupported for now, but it is ' \
                             'something that will be implemented in the future. '

    name, graph = list(graphs.items())[0]

    return console_run(graph)


def register(parser):
    parser.add_argument('file', type=argparse.FileType())
    return execute
