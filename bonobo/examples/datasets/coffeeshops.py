import sys

import bonobo
from bonobo import examples
from bonobo.contrib.opendatasoft import OpenDataSoftAPI as ODSReader
from bonobo.examples import get_services
from bonobo.structs.graphs import PartialGraph


def get_graph(graph=None, *, _limit=(), _print=()):
    graph = graph or bonobo.Graph()

    producer = (
        graph.get_cursor()
        >> ODSReader(dataset="liste-des-cafes-a-un-euro", netloc="opendata.paris.fr")
        >> PartialGraph(*_limit)
        >> bonobo.UnpackItems(0)
        >> bonobo.Rename(name="nom_du_cafe", address="adresse", zipcode="arrondissement")
        >> bonobo.Format(city="Paris", country="France")
        >> bonobo.OrderFields(["name", "address", "zipcode", "city", "country", "geometry", "geoloc"])
        >> PartialGraph(*_print)
    )

    # Comma separated values.
    graph.get_cursor(producer.output) >> bonobo.CsvWriter(
        "coffeeshops.csv", fields=["name", "address", "zipcode", "city"], delimiter=","
    )

    # Standard JSON
    graph.get_cursor(producer.output) >> bonobo.JsonWriter(path="coffeeshops.json")

    # Line-delimited JSON
    graph.get_cursor(producer.output) >> bonobo.LdjsonWriter(path="coffeeshops.ldjson")

    return graph


if __name__ == "__main__":
    sys.exit(examples.run(get_graph, get_services))
