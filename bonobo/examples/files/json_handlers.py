import bonobo
from bonobo.examples.files._services import get_services


def get_graph(*, _limit=None, _print=False):
    graph = bonobo.Graph()

    trunk = graph.add_chain(bonobo.JsonReader('datasets/theaters.json'), *((bonobo.Limit(_limit),) if _limit else ()))

    if _print:
        graph.add_chain(bonobo.PrettyPrinter(), _input=trunk.output)

    graph.add_chain(bonobo.JsonWriter('theaters.json', fs='fs.output'), _input=trunk.output)
    graph.add_chain(bonobo.LdjsonWriter('theaters.ldjson', fs='fs.output'), _input=trunk.output)

    return graph


if __name__ == '__main__':
    parser = bonobo.get_argument_parser()

    parser.add_argument('--limit', '-l', type=int, default=None, help='If set, limits the number of processed lines.')
    parser.add_argument(
        '--print', '-p', action='store_true', default=False, help='If set, pretty prints before writing to output file.'
    )

    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(_limit=options['limit'], _print=options['print']), services=get_services())
