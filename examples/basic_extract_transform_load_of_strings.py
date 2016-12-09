from bonobo.core.graph import Graph
from bonobo.core.strategy import NaiveStrategy, ExecutorStrategy


def extract():
    yield 'foo'
    yield 'bar'
    yield 'baz'


def transform(s):
    return s.title()


def load(s):
    print(s)


if __name__ == '__main__':
    etl = Graph()
    etl.add_chain(extract, transform, load)

    s = NaiveStrategy()
    s.execute(etl)

    s = ExecutorStrategy()
    s.execute(etl)
