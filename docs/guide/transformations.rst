Transformations
===============

Transformations are the smallest building blocks in |bonobo|.

There is no special data-structure used to represent transformations, it's basically just a regular python callable, or
even an iterable object (if it requires no input data).

Once in a graph, transformations become nodes and the data-flow between them is described using edges.


.. note::

    In this chapter, we'll consider that anytime we need a "database", it's something we can get from the global
    namespace. This practice OK-ish for small jobs, but not at scale.

    You'll learn in :doc:`services` how to manage external dependencies the right way.

Transformation types
::::::::::::::::::::

General case
------------

The **general case** is a transformation that yields n outputs for each input.

You can implement it using a generator:

.. code-block:: python

    db = ...

    def get_orders(user_id):
        for order in db.get_orders(user_id):
            yield user_id, order

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEFORE [shape=record label="0|1|<current>2|3|…" fontname="Courier New" fontsize=8 margin=0.03 width=0.3 style=filled fillcolor="#fafafa"];
        AFTER [shape=record label="{0|order#98}|{<current>2|order#42}|{2|order#43}|{3|order#11}|{3|order#12}|{3|order#16}|{3|order#18}|…" fontname="Courier New" fontsize=8 margin=0.03 width=0.3 style=filled fillcolor="#fafafa"];
        BEFORE:current -> "get_orders()" -> AFTER:current;

        db [shape=cylinder label="" width=0.5 height=0.4];
        db -> "get_orders()" [arrowhead=onormal];
        { rank = same; "get_orders()" db }
    }

*Here, each row (containing a user id) will be transformed into a set of rows, each containing an user_id and an "order"
object.*

Extractor case
--------------

An **extractor** is a transformation that generates output without using any input. Usually, it does not generate this
data out of nowhere, but instead connects to an external system (database, api, http, files ...) to read the data from
there.

It can be implemented in two different ways.

* You can implement it using a generator, like in the general case:

.. code-block:: python

    db = ...

    def extract_user_ids():
        yield from db.select_all_user_ids()

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape=point];
        AFTER [shape=record label="<f0>0|1|2|3|…" fontname="Courier New" fontsize=8 margin=0.03 width=0.3 style=filled fillcolor="#fafafa"];
        BEGIN -> "extract_user_ids()" -> AFTER:f0;


        db [shape=cylinder label="" width=0.5 height=0.4];
        db -> "extract_user_ids()" [arrowhead=onormal];
        { rank = same; "extract_user_ids()" db }
    }

* You can also use an iterator directly:

.. code-block:: python

    import bonobo

    db = ...

    def get_graph():
        graph = bonobo.Graph()
        graph.add_chain(
            db.select_all_user_ids(),
            ...
        )
        return graph

It is very convenient in many cases, when your existing system already have an interface that gives you iterators.

.. note::

   It's important to use a generative approach that yield data as it is provided and not generate everything
   at once before returning, so |bonobo| can pass the data to the next nodes as soon as it starts streaming.

Loader case
-----------

A **loader** is a transformation that sends its input into an external system. To have a perfect symmetry with
extractors, we'd like not to have any output but as a convenience and because it has a negligible cost
in |bonobo|, the convention is that all loaders return :obj:`bonobo.constants.NOT_MODIFIED`, meaning that all rows that
streamed into this node's input will also stream into its outputs, not modified. It allows to chain transformations even
after a loader happened, and avoid using shenanigans to achieve the same thing:

.. code-block:: python

   from bonobo.constants import NOT_MODIFIED

   analytics_db = ...

   def load_into_analytics_db(user_id, order):
       analytics_db.insert_or_update_order(user_id, order['id'], order['amount'])
       return NOT_MODIFIED


.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEFORE [shape=record label="{0|order#98}|{2|<current>order#42}|{2|order#43}|{3|order#11}|{3|order#12}|{3|order#16}|{3|order#18}|…" fontname="Courier New" fontsize=8 margin=0.03 width=0.3 style=filled fillcolor="#fafafa"];
        AFTER [shape=record label="{0|order#98}|{<current>2|order#42}|{2|order#43}|{3|order#11}|{3|order#12}|{3|order#16}|{3|order#18}|…" fontname="Courier New" fontsize=8 margin=0.03 width=0.3 style=filled fillcolor="#fafafa"];
        BEFORE:current -> "load_into_analytics_db()";
        "load_into_analytics_db()" -> AFTER:current [label="NOT_MODIFIED" fontsize=8 fontname="Courier New"];

        db [shape=cylinder label="" width=0.5 height=0.4];
        db -> "load_into_analytics_db()" [arrowtail=onormal dir=back];
        { rank = same; "load_into_analytics_db()" db }
    }


Execution Context
:::::::::::::::::

Transformations being regular functions, a bit of machinery is required to use them as nodes in a streaming flow.

When a :class:`bonobo.Graph` is executed, each node is wrapped in a
:class:`bonobo.execution.contexts.NodeExecutionContext` which is responsible for keeping the state of a node, within a
given execution.


Inputs and Outputs
::::::::::::::::::

When run in an execution context, transformations have inputs and outputs, which means that |bonobo| will pass data
that comes in the input queue as calls, and push returned / yielded values into the output queue.


.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        "Input Queue" [shape=record label="{|||||}" margin=0.03 width=1 style=filled fillcolor="#fafafa" height=0.25];
        "Output Queue" [shape=record label="{|||||}" margin=0.03 width=1 style=filled fillcolor="#fafafa" height=0.25];

        "Input Queue" -> "transformation" [label="input"];
         "transformation" -> "Output Queue" [label="output"];
    }

For thread-based strategies, the underlying implementation if the input and output queues is the standard
:class:`queue.Queue`.


Inputs
------

.. todo:: proofread, check consistency and correctness

All input is retrieved via the call arguments. Each line of input means one call to the callable provided. Arguments
will be, in order:

* Injected dependencies (database, http, filesystem, ...)
* Position based arguments
* Keyword based arguments

You'll see below how to pass each of those.

Output
------

.. todo:: proofread, check consistency and correctness

Each callable can return/yield different things (all examples will use yield, but if there is only one output per input
line, you can also return your output row and expect the exact same behaviour).

.. todo:: add rules for output parsing

The logic is defined in this piece of code, documentation will be added soon:

.. literalinclude:: ../../bonobo/execution/contexts/node.py
    :caption: NodeExecutionContext._cast(self, _input, _output)
    :pyobject: NodeExecutionContext._cast

Basically, after checking a few flags (`NOT_MODIFIED`, then `INHERIT`), it will "cast" the data into the "output type",
which is either tuple or a kind of namedtuple.

.. todo:: document cast/input_type/output_type logic.

Class-based Transformations
:::::::::::::::::::::::::::

For use cases that are either less simple or that requires better reusability, you may want to use classes to define
some of your transformations.

.. todo:: narrative doc

See:

* :class:`bonobo.config.Configurable`
* :class:`bonobo.config.Option`
* :class:`bonobo.config.Service`
* :class:`bonobo.config.Method`
* :class:`bonobo.config.ContextProcessor`


Naming conventions
::::::::::::::::::

The naming convention used is the following.

If you're naming something which is an actual transformation, that can be used directly as a graph node, then use
underscores and lowercase names:

.. code-block:: python

    # instance of a class based transformation
    filter = Filter(...)

    # function based transformation
    def uppercase(s: str) -> str:
        return s.upper()

If you're naming something which is configurable, that will need to be instantiated or called to obtain something that
can be used as a graph node, then use camelcase names:

.. code-block:: python

    # configurable
    class ChangeCase(Configurable):
        modifier = Option(default='upper')
        def __call__(self, s: str) -> str:
            return getattr(s, self.modifier)()

    # transformation factory
    def Apply(method):
        @functools.wraps(method)
        def apply(s: str) -> str:
            return method(s)
        return apply

    # result is a graph node candidate
    upper = Apply(str.upper)


Testing
:::::::

As Bonobo use plain old python objects as transformations, it's very easy to unit test your transformations using your
favourite testing framework. We're using pytest internally for Bonobo, but it's up to you to use the one you prefer.

If you want to test a transformation with the surrounding context provided (for example, service instances injected, and
context processors applied), you can use :class:`bonobo.execution.NodeExecutionContext` as a context processor and have
bonobo send the data to your transformation.


.. code-block:: python

    from bonobo.execution import NodeExecutionContext

    with NodeExecutionContext(
        JsonWriter(filename), services={'fs': ...}
    ) as context:
        # Write a list of rows, including BEGIN/END control messages.
        context.write_sync(
            {'foo': 'bar'},
            {'foo': 'baz'},
        )


.. include:: _next.rst
