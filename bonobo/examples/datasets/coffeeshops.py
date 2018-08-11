import bonobo
from bonobo import examples
from bonobo.contrib.opendatasoft import OpenDataSoftAPI as ODSReader
from bonobo.examples.datasets.services import get_services


def get_graph(graph=None, *, _limit=(), _print=()):
    """
    Extracts a list of cafes with on euro in Paris, renames the name, address and zipcode fields,
    reorders the fields and formats to json and csv files.

    """
    graph = graph or bonobo.Graph()

    producer = graph.add_chain(
        ODSReader(dataset='liste-des-cafes-a-un-euro', netloc='opendata.paris.fr'),
        *_limit,
        bonobo.UnpackItems(0),
        bonobo.Rename(name='nom_du_cafe', address='adresse', zipcode='arrondissement'),
        bonobo.Format(city='Paris', country='France'),
        bonobo.OrderFields(['name', 'address', 'zipcode', 'city', 'country', 'geometry', 'geoloc']),
        *_print,
    )

    # Comma separated values.
    graph.add_chain(
        bonobo.CsvWriter('coffeeshops.csv', fields=['name', 'address', 'zipcode', 'city'], delimiter=','),
        _input=producer.output,
    )

    # Standard JSON
    graph.add_chain(bonobo.JsonWriter(path='coffeeshops.json'), _input=producer.output)

    # Line-delimited JSON
    graph.add_chain(bonobo.LdjsonWriter(path='coffeeshops.ldjson'), _input=producer.output)

    return graph


if __name__ == '__main__':
    parser = examples.get_argument_parser()

    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**examples.get_graph_options(options)), services=get_services())
