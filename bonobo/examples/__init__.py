import bonobo


def get_argument_parser(parser=None):
    parser = bonobo.get_argument_parser(parser=parser)

    parser.add_argument('--limit', '-l', type=int, default=None, help='If set, limits the number of processed lines.')
    parser.add_argument(
        '--print', '-p', action='store_true', default=False, help='If set, pretty prints before writing to output file.'
    )

    return parser


def get_graph_options(options):
    _limit = options.pop('limit', None)
    _print = options.pop('print', False)

    return {'_limit': (bonobo.Limit(_limit),) if _limit else (), '_print': (bonobo.PrettyPrinter(),) if _print else ()}
