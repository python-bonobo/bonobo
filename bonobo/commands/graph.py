import json

from bonobo.util.objects import get_name
from bonobo.commands.run import read_file
from bonobo.constants import BEGIN


def execute(file):
    graph, plugins, services = read_file(file)

    print('digraph {')
    print('  rankdir = LR;')
    print('  "BEGIN" [shape="point"];')
    for i in graph.outputs_of(BEGIN):
        print('  "BEGIN" -> ' + json.dumps(get_name(graph.nodes[i])) + ';')
    print('}')


def register(parser):
    import argparse
    parser.add_argument('file', type=argparse.FileType())
    return execute
