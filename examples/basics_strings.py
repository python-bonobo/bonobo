import time
from random import randint

from bonobo.core.graphs import Graph


def extract():
    yield 'foo'
    yield 'bar'
    yield 'baz'


def transform(s):
    wait = randint(0, 1)
    time.sleep(wait)
    return s.title() + ' ' + str(wait)


def load(s):
    print(s)


graph = Graph()
graph.add_chain(extract, transform, load)

if __name__ == '__main__':
    from bonobo import run

    run(graph)
