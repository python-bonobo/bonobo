import json

from bonobo.commands.run import read, register_generic_run_arguments
from bonobo.constants import BEGIN
from bonobo.util.objects import get_name

OUTPUT_GRAPHVIZ = 'graphviz'


def _ident(graph, i):
    escaped_index = str(i)
    escaped_name = json.dumps(get_name(graph[i]))
    return '{{{} [label={}]}}'.format(escaped_index, escaped_name)


def execute(*, output, **kwargs):
    graph, plugins, services = read(**kwargs)

    if output == OUTPUT_GRAPHVIZ:
        print('digraph {')
        print('  rankdir = LR;')
        print('  "BEGIN" [shape="point"];')

        for i in graph.outputs_of(BEGIN):
            print('  "BEGIN" -> ' + _ident(graph, i) + ';')

        for ix in graph.topologically_sorted_indexes:
            for iy in graph.outputs_of(ix):
                print('  {} -> {};'.format(_ident(graph, ix), _ident(graph, iy)))

        print('}')
    else:
        raise NotImplementedError('Output type not implemented.')


def register(parser):
    register_generic_run_arguments(parser)
    parser.add_argument('--graph', '-g', dest='output', action='store_const', const=OUTPUT_GRAPHVIZ)
    parser.set_defaults(output=OUTPUT_GRAPHVIZ)
    return execute
