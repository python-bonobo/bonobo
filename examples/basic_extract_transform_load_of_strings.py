from bonobo.strategy import NaiveStrategy, ExecutorStrategy

from bonobo.core.graph import Graph


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


