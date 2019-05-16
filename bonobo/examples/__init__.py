import os

import bonobo
from bonobo.execution.strategies import DEFAULT_STRATEGY, STRATEGIES
from bonobo.util.statistics import Timer


def get_argument_parser(parser=None):
    parser = bonobo.get_argument_parser(parser=parser)

    parser.add_argument("--limit", "-l", type=int, default=None, help="If set, limits the number of processed lines.")
    parser.add_argument(
        "--print", "-p", action="store_true", default=False, help="If set, pretty prints before writing to output file."
    )

    parser.add_argument("--strategy", "-s", type=str, choices=STRATEGIES.keys(), default=DEFAULT_STRATEGY)

    return parser


def get_graph_options(options):
    _limit = options.pop("limit", None)
    _print = options.pop("print", False)

    return {"_limit": (bonobo.Limit(_limit),) if _limit else (), "_print": (bonobo.PrettyPrinter(),) if _print else ()}


def run(get_graph, get_services, *, parser=None):
    parser = parser or get_argument_parser()

    with bonobo.parse_args(parser) as options:
        with Timer() as timer:
            print("Options:", " ".join("{}={}".format(k, v) for k, v in sorted(options.items())))
            retval = bonobo.run(
                get_graph(**get_graph_options(options)), services=get_services(), strategy=options["strategy"]
            )
        print("Execution time:", timer)
        print("Return value:", retval)
        print("XStatus:", retval.xstatus)
        return retval.xstatus


def get_minor_version():
    return ".".join(bonobo.__version__.split(".")[:2])


def get_datasets_dir(*dirs):
    home_dir = os.path.expanduser("~")
    target_dir = os.path.join(home_dir, ".cache/bonobo", get_minor_version(), *dirs)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def get_services():
    return {
        "fs": bonobo.open_fs(get_datasets_dir("datasets")),
        "fs.static": bonobo.open_examples_fs("datasets", "static"),
    }
