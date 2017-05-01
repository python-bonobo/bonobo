"""
Simple example of :func:`bonobo.count` usage.

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "range()" -> "count" -> "print";
    }

"""

import bonobo

graph = bonobo.Graph(range(42), bonobo.count, print)

if __name__ == '__main__':
    bonobo.run(graph)
