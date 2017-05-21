"""
Example on how to use symple python strings to communicate between transformations.

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "extract()" -> "transform(s: str)" -> "load(s: str)";
    }

"""
from random import randint

from bonobo import Graph


def extract():
    yield 'foo'
    yield 'bar'
    yield 'baz'


def transform(s: str):
    return '{} ({})'.format(s.title(), randint(10, 99))


def load(s: str):
    print(s)


graph = Graph(extract, transform, load)

if __name__ == '__main__':
    from bonobo import run

    run(graph)
