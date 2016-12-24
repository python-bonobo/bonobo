import time
from random import randint

from bonobo.core.graphs import Graph
from bonobo.core.strategies.executor import ThreadPoolExecutorStrategy
from bonobo.ext.console import ConsoleOutputPlugin


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


Strategy = ThreadPoolExecutorStrategy

if __name__ == '__main__':
    etl = Graph()
    etl.add_chain(extract, transform, load)

    s = Strategy()
    s.execute(etl, plugins=[ConsoleOutputPlugin()])
