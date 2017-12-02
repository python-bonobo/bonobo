import bonobo
from bonobo import examples
from bonobo.examples.datasets.coffeeshops import get_graph as get_coffeeshops_graph
from bonobo.examples.datasets.fablabs import get_graph as get_fablabs_graph
from bonobo.examples.datasets.services import get_services

graph_factories = {
    'coffeeshops': get_coffeeshops_graph,
    'fablabs': get_fablabs_graph,
}

if __name__ == '__main__':
    parser = examples.get_argument_parser()
    parser.add_argument(
        '--target', '-t', choices=graph_factories.keys(), nargs='+'
    )

    with bonobo.parse_args(parser) as options:
        graph_options = examples.get_graph_options(options)
        graph_names = list(
            options['target']
            if options['target'] else sorted(graph_factories.keys())
        )

        graph = bonobo.Graph()
        for name in graph_names:
            graph = graph_factories[name](graph, **graph_options)

        bonobo.run(graph, services=get_services())
