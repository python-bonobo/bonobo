"""
Example on how to use symple python dictionaries to communicate between transformations.

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "extract()" -> "transform(row: dict)" -> "load(row: dict)";
    }

"""

from random import randint

from bonobo import Graph


def extract():
    yield {'topic': 'foo'}
    yield {'topic': 'bar'}
    yield {'topic': 'baz'}


def transform(row: dict):
    return {
        'topic': row['topic'].title(),
        'randint': randint(10, 99),
    }


def load(row: dict):
    print(row)


graph = Graph(extract, transform, load)

if __name__ == '__main__':
    from bonobo import run

    run(graph)
