import sys

import bonobo
from bonobo import examples
from bonobo.examples.files.services import get_services


def get_graph(*, _limit=None, _print=False):
    return bonobo.Graph(
        bonobo.CsvReader("coffeeshops.csv"),
        *((bonobo.Limit(_limit),) if _limit else ()),
        *((bonobo.PrettyPrinter(),) if _print else ()),
        bonobo.CsvWriter("coffeeshops.csv", fs="fs.output")
    )


if __name__ == "__main__":
    sys.exit(examples.run(get_graph, get_services))
