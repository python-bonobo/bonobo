"""
Example on how to use :class:`bonobo.Bag` instances to pass flexible args/kwargs to the next callable.

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "extract()" -> "transform(...)" -> "load(...)";
    }

"""

from random import randint

from bonobo import Bag, Graph


def extract():
    yield Bag(topic='foo')
    yield Bag(topic='bar')
    yield Bag(topic='baz')


def transform(topic: str):
    return Bag.inherit(title=topic.title(), rand=randint(10, 99))


def load(topic: str, title: str, rand: int):
    print('{} ({}) wait={}'.format(title, topic, rand))


graph = Graph()
graph.add_chain(extract, transform, load)

if __name__ == '__main__':
    from bonobo import run

    run(graph)
