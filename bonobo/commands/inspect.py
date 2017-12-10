import json

from bonobo.commands.run import read, register_generic_run_arguments
from bonobo.constants import BEGIN
from bonobo.util.objects import get_name
import webbrowser
import os
OUTPUT_GRAPHVIZ = 'graphviz'


def _ident(graph, i):
    escaped_index = str(i)
    escaped_name = json.dumps(get_name(graph[i]))
    return '{{{} [label={}]}}'.format(escaped_index, escaped_name)


def execute(*, output,open_in_browser,**kwargs):
    graph, plugins, services = read(**kwargs)
    graphviz_dot = ''
    if output == OUTPUT_GRAPHVIZ:
        graphviz_dot += 'digraph {'
        graphviz_dot += '  rankdir = LR;'
        graphviz_dot +='  "BEGIN" [shape="point"];'

        for i in graph.outputs_of(BEGIN):
            graphviz_dot += '  "BEGIN" -> ' + _ident(graph, i) + ';'

        for ix in graph.topologically_sorted_indexes:
            for iy in graph.outputs_of(ix):
                graphviz_dot += '  {} -> {};'.format(_ident(graph, ix), _ident(graph, iy))

        graphviz_dot += '}'
    else:
        raise NotImplementedError('Output type not implemented.')

    if open_in_browser:
        with open('viz.js/viz-template.html','r') as f:
            template = f.read()
        with open('viz.js/viz.html','w') as f:
            f.write(template.replace('GRAPHVIZ_SOURCE_TOKEN',graphviz_dot))
        browser = webbrowser.open(url=r'file:///' + os.path.dirname(os.path.realpath(  __file__ )) + '/viz.js/viz.html',new=1, autoraise=True)
    print(graphviz_dot)



def register(parser):
    register_generic_run_arguments(parser)
    parser.add_argument('--graph', '-g', dest='output', action='store_const', const=OUTPUT_GRAPHVIZ)
    parser.add_argument('--open', '-O', dest='open_in_browser', action='store_true')
    parser.set_defaults(output=OUTPUT_GRAPHVIZ,open_in_browser=False)
    return execute
