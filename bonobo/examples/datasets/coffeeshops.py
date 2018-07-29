"""

"""
import sys

import bonobo
from bonobo import examples
from bonobo.contrib.opendatasoft import OpenDataSoftAPI as ODSReader
from bonobo.examples import get_services


def get_graph(graph=None, *, _limit=(), _print=()):
    graph = graph or bonobo.Graph()

    producer = graph.add_chain(
        ODSReader(
            dataset='liste-des-cafes-a-un-euro',
            netloc='opendata.paris.fr'
        ),
        *_limit,
        bonobo.UnpackItems(0),
        bonobo.Rename(
            name='nom_du_cafe',
            address='adresse',
            zipcode='arrondissement'
        ),
        bonobo.Format(city='Paris', country='France'),
        bonobo.OrderFields(
            [
                'name', 'address', 'zipcode', 'city', 'country',
                'geometry', 'geoloc'
            ]
        ),
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


if __name__ == '__main__':
    sys.exit(examples.run(get_graph, get_services))
