Graphs
======

Graphs are the glue that ties transformations together. It's the only data-structure bonobo can execute directly. Graphs
must be acyclic, and can contain as much nodes as your system can handle. Although this number can be rather high in
theory, extreme practical cases usually do not exceed hundreds of nodes (and this is already extreme, really).


Definitions
:::::::::::

Graph

    A directed acyclic graph of transformations, that Bonobo can inspect and execute.

Node

    A transformation within a graph. The transformations are stateless, and have no idea whether or not they are
    included in a graph, multiple graph, or not at all.


Creating a graph
::::::::::::::::

Graphs should be instances of :class:`bonobo.Graph`. The :func:`bonobo.Graph.add_chain` method can take as many
positional parameters as you want.

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()
    graph.add_chain(a, b, c)

Resulting graph:

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "a" -> "b" -> "c";
    }

Non-linear graphs
:::::::::::::::::

Divergences / forks
-------------------

To create two or more divergent data streams ("fork"), you should specify `_input` kwarg to `add_chain`.

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()
    graph.add_chain(a, b, c)
    graph.add_chain(f, g, _input=b)


Resulting graph:

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "a" -> "b" -> "c";
        "b" -> "f" -> "g";
    }

.. note:: Both branch will receive the same data, at the same time.

Convergences / merges
---------------------

To merge two data streams ("merge"), you can use the `_output` kwarg to `add_chain`, or use named nodes (see below).


.. code-block:: python

    import bonobo

    graph = bonobo.Graph()

    # Here we mark _input to None, so normalize won't get the "begin" impulsion.
    graph.add_chain(normalize, store, _input=None)

    # Add two different chains
    graph.add_chain(a, b, _output=normalize)
    graph.add_chain(f, g, _output=normalize)


Resulting graph:

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "a" -> "b" -> "normalize";

        BEGIN2 [shape="point"];
        BEGIN2 -> "f" -> "g" -> "normalize";

        "normalize" -> "store"
    }

.. note::

    This is not a "join" or "cartesian product". Any data that comes from `b` or `g` will go through `normalize`, one at
    a time. Think of the graph edges as data flow pipes.


Named nodes
:::::::::::

Using above code to create convergences can lead to hard to read code, because you have to define the "target" stream
before the streams that logically goes to the beginning of the transformation graph. To overcome that, one can use
"named" nodes:

    graph.add_chain(x, y, z, _name='zed')
    graph.add_chain(f, g, h, _input='zed')

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()

    # Add two different chains
    graph.add_chain(a, b, _output="load")
    graph.add_chain(f, g, _output="load")

    # Here we mark _input to None, so normalize won't get the "begin" impulsion.
    graph.add_chain(normalize, store, _input=None, _name="load")


Resulting graph:

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "a" -> "b" -> "normalize (load)";

        BEGIN2 [shape="point"];
        BEGIN2 -> "f" -> "g" -> "normalize (load)";

        "normalize (load)" -> "store"
    }


Inspecting graphs
:::::::::::::::::

Bonobo is bundled with an "inspector", that can use graphviz to let you visualize your graphs.

Read `How to inspect and visualize your graph <https://www.bonobo-project.org/how-to/inspect-an-etl-jobs-graph>`_.


Executing graphs
::::::::::::::::

There are two options to execute a graph (which have a similar result, but are targeting different use cases).

* You can use the bonobo command line interface, which is the highest level interface.
* You can use the python API, which is lower level but allows to use bonobo from within your own code (for example, a
  django management command).

Executing a graph with the command line interface
-------------------------------------------------

If there is no good reason not to, you should use `bonobo run ...` to run transformation graphs found in your python
source code files.

.. code-block:: shell-session

    $ bonobo run file.py

You can also run a python module:

.. code-block:: shell-session

    $ bonobo run -m my.own.etlmod

In each case, bonobo's CLI will look for an instance of :class:`bonobo.Graph` in your file/module, create the plumbery
needed to execute it, and run it.

If you're in an interactive terminal context, it will use :class:`bonobo.ext.console.ConsoleOutputPlugin` for display.

If you're in a jupyter notebook context, it will (try to) use :class:`bonobo.ext.jupyter.JupyterOutputPlugin`.

Executing a graph using the internal API
----------------------------------------

To integrate bonobo executions in any other python code, you should use :func:`bonobo.run`. It behaves very similar to
the CLI, and reading the source you should be able to figure out its usage quite easily.



