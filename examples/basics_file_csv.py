import os

from bonobo import CsvReader, Graph

__path__ = os.path.dirname(__file__)


def skip_comments(line):
    if not line.startswith('#'):
        yield line


graph = Graph(
    CsvReader(path=os.path.join(__path__, 'datasets/coffeeshops.txt')),
    print,
)

if __name__ == '__main__':
    import bonobo

    bonobo.run(graph)
