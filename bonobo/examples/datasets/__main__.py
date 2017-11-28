import bonobo
from bonobo import examples
from bonobo.contrib.opendatasoft import OpenDataSoftAPI as ODSReader
from bonobo.nodes.basics import UnpackItems, Rename, Format


def get_coffeeshops_graph(graph=None, *, _limit=(), _print=()):
    graph = graph or bonobo.Graph()

    producer = graph.add_chain(
        ODSReader(
            dataset='liste-des-cafes-a-un-euro',
            netloc='opendata.paris.fr'
        ),
        *_limit,
        UnpackItems(0),
        Rename(
            name='nom_du_cafe',
            address='adresse',
            zipcode='arrondissement'
        ),
        Format(city='Paris', country='France'),
        *_print,
    )

    # Comma separated values.
    graph.add_chain(
        bonobo.CsvWriter(
            'coffeeshops.csv',
            fields=['name', 'address', 'zipcode', 'city'],
            delimiter=','
        ),
        _input=producer.output,
    )

    # Name to address JSON
    # graph.add_chain(
    #    bonobo.JsonWriter(path='coffeeshops.dict.json'),
    #    _input=producer.output,
    # )

    # Standard JSON
    graph.add_chain(
        bonobo.JsonWriter(path='coffeeshops.json'),
        _input=producer.output,
    )

    # Line-delimited JSON
    graph.add_chain(
        bonobo.LdjsonWriter(path='coffeeshops.ldjson'),
        _input=producer.output,
    )

    return graph


all = 'all'
graphs = {
    'coffeeshops': get_coffeeshops_graph,
}


def get_services():
    return {'fs': bonobo.open_fs(bonobo.get_examples_path('datasets'))}


if __name__ == '__main__':
    parser = examples.get_argument_parser()
    parser.add_argument('--target', '-t', choices=graphs.keys(), nargs='+')

    with bonobo.parse_args(parser) as options:
        graph_options = examples.get_graph_options(options)
        graph_names = list(options['target'] if options['target'] else sorted(graphs.keys()))

        graph = bonobo.Graph()
        for name in graph_names:
            graph = graphs[name](graph, **graph_options)

        bonobo.run(graph, services=get_services())
