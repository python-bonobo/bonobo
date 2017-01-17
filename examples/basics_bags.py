import time
from random import randint

from bonobo import Bag
from bonobo.core.graphs import Graph


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


graph = Graph()
graph.add_chain(extract, transform, load)

if __name__ == '__main__':
    from bonobo.util.helpers import run

    run(graph)
