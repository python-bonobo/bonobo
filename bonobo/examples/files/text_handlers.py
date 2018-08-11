import bonobo
from bonobo import examples
from bonobo.examples.files._services import get_services


def skip_comments(line):
    line = line.strip()
    if not line.startswith('#'):
        yield line


def get_graph(*, _limit=(), _print=()):
    return bonobo.Graph(
        bonobo.FileReader('datasets/passwd.txt'),
        skip_comments,
        *_limit,
        lambda s: s.split(':')[0],
        *_print,
        bonobo.FileWriter('usernames.txt', fs='fs.output'),
    )


if __name__ == '__main__':
    parser = examples.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**examples.get_graph_options(options)), services=get_services())
