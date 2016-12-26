import time
from random import randint

from bonobo import Bag
from bonobo.core.graphs import Graph
from bonobo.core.strategies.executor import ThreadPoolExecutorStrategy
from bonobo.ext.console import ConsoleOutputPlugin


def extract():
    yield Bag(topic='foo')
    yield Bag(topic='bar')
    yield Bag(topic='baz')


def transform(topic: str):
    wait = randint(0, 1)
    time.sleep(wait)
    return Bag.inherit(title=topic.title(), wait=wait)


def load(topic: str, title: str, wait: int):
    print('{} ({}) wait={}'.format(title, topic, wait))


Strategy = ThreadPoolExecutorStrategy

if __name__ == '__main__':
    etl = Graph()
    etl.add_chain(extract, transform, load)

    s = Strategy()
    s.execute(etl, plugins=[ConsoleOutputPlugin()])
