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

import bonobo


def extract():
    yield 'foo'
    yield 'bar'
    yield 'baz'


def transform(s):
    return '{} ({})'.format(s.title(), randint(10, 99))


def load(s):
    print(s)


def get_graph():
    return bonobo.Graph(extract, transform, load)


if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser):
        bonobo.run(get_graph())
