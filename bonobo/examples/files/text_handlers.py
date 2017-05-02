import bonobo
from bonobo.commands.run import get_default_services


def skip_comments(line):
    if not line.startswith('#'):
        yield line


graph = bonobo.Graph(
    bonobo.FileReader('datasets/passwd.txt'),
    skip_comments,
    lambda s: s.split(':'),
    lambda l: l[0],
    print,
)

if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__))
