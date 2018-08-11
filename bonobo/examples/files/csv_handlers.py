import bonobo
from bonobo.examples.files._services import get_services


def get_graph(*, _limit=None, _print=False):
    return bonobo.Graph(
        bonobo.CsvReader('datasets/coffeeshops.txt'),
        *((bonobo.Limit(_limit),) if _limit else ()),
        *((bonobo.PrettyPrinter(),) if _print else ()),
        bonobo.CsvWriter('coffeeshops.csv', fs='fs.output')
    )


if __name__ == '__main__':
    parser = bonobo.get_argument_parser()

    parser.add_argument('--limit', '-l', type=int, default=None, help='If set, limits the number of processed lines.')
    parser.add_argument(
        '--print', '-p', action='store_true', default=False, help='If set, pretty prints before writing to output file.'
    )

    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(_limit=options['limit'], _print=options['print']), services=get_services())
