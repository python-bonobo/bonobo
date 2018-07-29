import sys

import bonobo
from bonobo import examples
from bonobo.examples.files.services import get_services


def skip_comments(line):
    line = line.strip()
    if not line.startswith("#"):
        yield line


def get_graph(*, _limit=(), _print=()):
    return bonobo.Graph(
        bonobo.FileReader("passwd.txt", fs="fs.static"),
        skip_comments,
        *_limit,
        lambda s: s.split(":")[0],
        *_print,
        bonobo.FileWriter("usernames.txt", fs="fs.output"),
    )


if __name__ == "__main__":
    sys.exit(examples.run(get_graph, get_services))
