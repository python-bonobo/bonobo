import sys

import bonobo
from bonobo import examples
from bonobo.examples.files.services import get_services


def get_graph(*, _limit=None, _print=False):
    graph = bonobo.Graph()

    trunk = graph.add_chain(
        bonobo.JsonReader("theaters.json", fs="fs.static"), *((bonobo.Limit(_limit),) if _limit else ())
    )

    if _print:
        graph.add_chain(bonobo.PrettyPrinter(), _input=trunk.output)

    graph.add_chain(bonobo.JsonWriter("theaters.output.json", fs="fs.output"), _input=trunk.output)
    graph.add_chain(bonobo.LdjsonWriter("theaters.output.ldjson", fs="fs.output"), _input=trunk.output)

    return graph


if __name__ == "__main__":
    sys.exit(examples.run(get_graph, get_services))
