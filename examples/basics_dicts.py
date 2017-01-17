import time
from random import randint

from bonobo.core.graphs import Graph


def extract():
    yield {'topic': 'foo'}
    yield {'topic': 'bar'}
    yield {'topic': 'baz'}


def transform(row):
    wait = randint(0, 1)
    time.sleep(wait)
    return {
        'topic': row['topic'].title(),
        'wait': wait,
    }


def load(s):
    print(s)


graph = Graph()
graph.add_chain(extract, transform, load)

if __name__ == '__main__':
    from bonobo import run

    run(graph)
