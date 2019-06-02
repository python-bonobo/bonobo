Graphs
======

Graphs are the glue that ties transformations together. They are the only data-structure bonobo can execute directly.
Graphs must be acyclic, and can contain as many nodes as your system can handle. However, although in theory the number
of nodes can be rather high, practical cases usually do not exceed a few hundred nodes and even that is a rather high
number you may not encounter so often.

Within a graph, each node are isolated and can only communicate using their input and output queues. For each input row,
a given node will be called with the row passed as arguments. Each *return* or *yield* value will be put on the node's
output queue, and the nodes connected in the graph will then be able to process it.

|bonobo| is a line-by-line data stream processing solution.

Handling the data-flow this way brings the following properties:

- **First in, first out**: unless stated otherwise, each node will receeive the rows from FIFO queues, and so, the order
  of rows will be preserved. That is true for each single node, but please note that if you define "graph bubbles"
  (where a graph diverge in different branches then converge again), the convergence node will receive rows FIFO from
  each input queue, meaning that the order existing at the divergence point wont stay true at the convergence point.

- **Parallelism**: each node run in parallel (by default, using independent threads). This is useful as you don't have
  to worry about blocking calls. If a thread waits for, let's say, a database, or a network service, the other nodes
  will continue handling data, as long as they have input rows available.

- **Independence**: the rows are independent from each other, making this way of working with data flows good for
  line-by-line data processing, but also not ideal for "grouped" computations (where an output depends on more than one
  line of input data). You can overcome this with rolling windows if the input required are adjacent rows, but if you
  need to work on the whole dataset at once, you should consider other software.

Graphs are defined using :class:`bonobo.Graph` instances, as seen in the previous tutorial step.


What can be used as a node?
:::::::::::::::::::::::::::

**TL;DR**: … anything, as long as it’s callable() or iterable.

Functions
---------

.. code-block:: python

    def get_item(id):
        return id, items.get(id)

When building your graph, you can simply add your function:

.. code-block:: python

    graph.add_chain(..., get_item, ...)

Or using the new syntax:

.. code-block:: python

    graph >> ... >> get_item >> ...

.. note::

    Please note that we pass the function object, and not the result of the function being called. A common mistake is
    to call the function while building the graph, which won't work and may be tedious to debug.

    As a convention, we use snake_cased objects when the object can be directly passed to a graph, like this function.

    Some functions are factories for closures, and thus behave differently (as you need to call them to get an actual
    object usable as a transformation. When it is the case, we use CamelCase as a convention, as it behaves the same way
    as a class.


Classes
-------

.. code-block:: python

    class Foo:
        ...

        def __call__(self, id):
            return id, self.get(id)

When building your graph, you can add an instance of your object (or even multiple instances, eventually configured
differently):

.. code-block:: python

    graph.add_chain(..., Foo(), ...)

Or using the new syntax:

.. code-block:: python

    graph >> ... >> Foo() >> ...


Iterables (generators, lists, ...)
----------------------------------

As a convenience tool, we can use iterables directly within a graph. It can either be used as producer nodes (nodes that
are normally only called once and produce data) or, in case of generators, as transformations.


.. code-block:: python

    def product(x):
        for i in range(10)
            yield x, i, x * i

Then, add it to a graph:

.. code-block:: python

    graph.add_chain(range(10), product, ...)

Or using the new syntax:

.. code-block:: python

    graph >> range(10) >> product >> ...


Builtins
--------

Again, as long as it is callable, you can use it as a node. It means that python builtins works (think about `print` or
`str.upper`...)

.. code-block:: python

    graph.add_chain(range(ord("a"), ord("z")+1), chr, str.upper, print)

Or using the new syntax:

.. code-block:: python

    graph >> range(ord("a"), ord("z")+1) >> chr >> str.upper >> print


What happens during the graph execution?
::::::::::::::::::::::::::::::::::::::::

Each node of a graph will be executed in isolation from the other nodes, and the data is passed from one node to the
next using FIFO queues, managed by the framework. It's transparent to the end-user, though, and you'll only use
function arguments (for inputs) and return/yield values (for outputs).

Each input row of a node will cause one call to this node's callable. Each output is cast internally as a tuple-like
data structure (or more precisely, a namedtuple-like data structure), and for one given node, each output row must
have the same structure.

If you return/yield something which is not a tuple, bonobo will create a tuple of one element.

Properties
----------

|bonobo| assists you with defining the data-flow of your data engineering process, and then streams data through your
callable graphs.

* Each node call will process one row of data.
* Queues that flows the data between node are first-in, first-out (FIFO) standard python :class:`queue.Queue`.
* Each node will run in parallel
* Default execution strategy use threading, and each node will run in a separate thread.

Fault tolerance
---------------

Node execution is fault tolerant.

If an exception is raised from a node call, then this node call will be aborted but bonobo will continue the execution
with the next row (after outputing the stack trace and incrementing the "err" counter for the node context).

It allows to have ETL jobs that ignore faulty data and try their best to process the valid rows of a dataset.

Some errors are fatal, though.

If you pass a 2 elements tuple to a node that takes 3 args, |bonobo| will raise an
:class:`bonobo.errors.UnrecoverableTypeError`, and exit the current graph execution as fast as it can (finishing the
other node executions that are in progress first, but not starting new ones if there are remaining input rows).


Definitions
:::::::::::

Graph

    A directed acyclic graph of transformations, that Bonobo can inspect and execute.

Node

    A transformation within a graph. The transformations are stateless, and have no idea whether or not they are
    included in a graph, multiple graph, or not at all.


Building graphs
:::::::::::::::

Graphs in |bonobo| are instances of :class:`bonobo.Graph`

Graphs should be instances of :class:`bonobo.Graph`. The :func:`bonobo.Graph.add_chain` method can take as many
positional parameters as you want.

.. note::

    As of |bonobo| 0.7, a new syntax is available that we believe is more powerfull and more readable than the legacy
    `add_chain` method. The former API is here to stay and it's perfectly safe to use it (in fact, the new syntax uses
    `add_chain` under the hood).
    
    If it is an option for you, we suggest you consider the new syntax. During the transition period, we'll document
    both but the new syntax will eventually become default.

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()
    graph.add_chain(a, b, c)

Or using the new syntax:

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()
    graph >> a >> b >> c


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

To create two or more divergent data streams ("forks"), you should specify the `_input` kwarg to `add_chain`.

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()
    graph.add_chain(a, b, c)
    graph.add_chain(f, g, _input=b)

Or using the new syntax:

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()
    graph >> a >> b >> c
    graph.get_cursor(b) >> f >> g


Resulting graph:

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "a" -> "b" -> "c";
        "b" -> "f" -> "g";
    }

.. note:: Both branches will receive the same data and at the same time.

Convergence / merges
---------------------

To merge two data streams, you can use the `_output` kwarg to `add_chain`, or use named nodes (see below).


.. code-block:: python

    import bonobo

    graph = bonobo.Graph()

    # Here we set _input to None, so normalize won't start on its own but only after it receives input from the other chains.
    graph.add_chain(normalize, store, _input=None)

    # Add two different chains
    graph.add_chain(a, b, _output=normalize)
    graph.add_chain(f, g, _output=normalize)

Or using the new syntax:

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()

    # Here we set _input to None, so normalize won't start on its own but only after it receives input from the other chains.
    graph.get_cursor(None) >> normalize >> store

    # Add two different chains
    graph >> a >> b >> normalize
    graph >> f >> g >> normalize


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

Using above code to create convergences often leads to code which is hard to read, because you have to define the "target" stream
before the streams that logically goes to the beginning of the transformation graph. To overcome that, one can use
"named" nodes.

Please note that naming a chain is exactly the same thing as naming the first node of a chain.

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()

    # Here we mark _input to None, so normalize won't get the "begin" impulsion.
    graph.add_chain(normalize, store, _input=None, _name="load")

    # Add two different chains that will output to the "load" node
    graph.add_chain(a, b, _output="load")
    graph.add_chain(f, g, _output="load")

Using the new syntax, there should not be a need to name nodes. Let us know if you think otherwise by creating an issue.


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

You can also create single nodes, and the api provide the same capability on single nodes. 

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()

    # Create a node without any connection, name it.
    graph.add_node(foo, _name="foo")

    # Use it somewhere else as the data source.
    graph.add_chain(..., _input="foo")

    # ... or as the data sink.
    graph.add_chain(..., _output="foo")


Orphan nodes / chains
:::::::::::::::::::::

The default behaviour of `add_chain` (or `get_cursor`) is to connect the first node to the special `BEGIN` token, which
instruct |bonobo| to call the connected node once without parameter to kickstart the data stream.

This is normally what you want, but there are ways to override it, as you may want to add "orphan" nodes or chains to your graph.

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()

    # using add_node will naturally add a node as "orphan"   
    graph.add_node(a)

    # using add_chain with "None" as the input will create an orphan chain
    graph.add_chain(a, b, c, _input=None)

    # using the new syntax, you can use either get_cursor(None) or the orphan() shortcut
    graph.get_cursor(None) >> a >> b >> c
    
    # ... using the shortcut ...
    graph.orphan() >> a >> b >> c


Connecting two nodes
::::::::::::::::::::

You may want to connect two nodes at some point. You can use `add_chain` without nodes to achieve it.

.. code-block:: python

    import bonobo

    graph = bonobo.Graph()

    # Create two "anonymous" nodes
    graph.add_node(a)
    graph.add_node(b)

    # Connect them
    graph.add_chain(_input=a, _output=b)

Or using the new syntax:

.. code-block:: python

    graph.get_cursor(a) >> b


Cursors
:::::::

Cursors are simple structures that references a graph, a starting point and a finishing point. They can be used to
manipulate graphs using the `>>` operator in an intuitive way.

To grab a cursor from a graph, you have different options:

.. code-block:: python

    # the most obvious way to get a cursor, its starting point will be "BEGIN"
    cursor = graph.get_cursor()

    # same thing, explicitely
    cursor = graph.get_cursor(BEGIN)

    # if you try to use a graph with the `>>` operator, it will create a cursor for you, from "BEGIN"
    cursor = graph >> ...  # same as `graph.get_cursor(BEGIN) >> ...`

    # get a cursor pointing to nothing
    cursor = graph.get_cursor(None)

    # ... or in a more readable way
    cursor = graph.orphan()    

Once you get a cursor, you can use it to add nodes, concatenate it with othe cursors, etc. Everytime you call something
that should result in a changed cursor, you'll get a new instance so your old cursor will still be available if you need
it.

.. code-block:: python

    c1 = graph.orphan()

    # append a node, get a new cursor
    c2 = c1 >> node1

    # create an orphan chain
    c3 = graph.orphan() >> normalize

    # concatenate a chain to an existing cursor
    c4 = c2 >> c3


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

In each case, bonobo's CLI will look for an instance of :class:`bonobo.Graph` in your file/module, create the plumbing
needed to execute it, and run it.

If you're in an interactive terminal context, it will use :class:`bonobo.ext.console.ConsoleOutputPlugin` for display.

If you're in a jupyter notebook context, it will (try to) use :class:`bonobo.ext.jupyter.JupyterOutputPlugin`.

Executing a graph using the internal API
----------------------------------------

To integrate bonobo executions in any other python code, you should use :func:`bonobo.run`. It behaves very similar to
the CLI, and reading the source you should be able to figure out its usage quite easily.



.. include:: _next.rst
