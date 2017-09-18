import json

import itertools

from bonobo.util.objects import get_name
from bonobo.commands.run import read, register_generic_run_arguments
from bonobo.constants import BEGIN


def execute(filename, module, install=False, quiet=False, verbose=False):
    graph, plugins, services = read(filename, module, install, quiet, verbose)

    print('digraph {')
    print('  rankdir = LR;')
    print('  "BEGIN" [shape="point"];')

    for i in graph.outputs_of(BEGIN):
        print('  "BEGIN" -> ' + json.dumps(get_name(graph[i])) + ';')

    for ix in graph.topologically_sorted_indexes:
        for iy in graph.outputs_of(ix):
            print('  {} -> {};'.format(
                json.dumps(get_name(graph[ix])),
                json.dumps(get_name(graph[iy]))
            ))

    print('}')


def register(parser):
    register_generic_run_arguments(parser)
    return execute
