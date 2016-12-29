Basic concepts
==============

To begin with Bonobo, you need to install it in a working python 3.5+ environment:

.. code-block:: shell-session

    $ pip install bonobo

See :doc:`/install` for more options.

Let's write a first data transformation
:::::::::::::::::::::::::::::::::::::::

We'll start with the most simple components we can.

In **Bonobo**, a component is a plain old python callable, not more, not less. Let's write one that takes a string and
uppercase it.

.. code-block:: python

    def uppercase(x: str):
        return x.upper()

Pretty straightforward.

You could even use :func:`str.upper` directly instead of writing a wrapper, as a type's method (unbound) will take an
instance of this type as its first parameter (what you'd call `self` in your method).

The type annotations written here are not used, but can make your code much more readable, and may very well be used as
validators in the future.

Let's write two more components: a generator to produce the data to be transformed, and something that outputs it,
because, yeah, feedback is cool.

.. code-block:: python

    def generate_data():
        yield 'foo'
        yield 'bar'
        yield 'baz'

    def output(x: str):
        print(x)

Once again, you could have skipped the pain of writing this and simply use an iterable to generate the data and the
builtin :func:`print` for the output, but we'll stick to writing our own components for now.

Let's chain the three components together and run the transformation:

.. code-block:: python

    from bonobo import run

    run(generate_data, uppercase, output)

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "generate_data" -> "uppercase" -> "output";
    }

We use the :func:`bonobo.run` helper that hides the underlying object composition necessary to actually run the
components in parralel, because it's simpler.

Depending on what you're doing, you may use the shorthand helper method, or the verbose one. Always favor the shorter,
if you don't need to tune the graph or the execution strategy (see below).

Diving in
:::::::::

Let's rewrite it using the builtin functions :func:`str.upper` and :func:`print` instead of our own wrappers, and expand
the :func:`bonobo.run()` helper so you see what's inside...

.. code-block:: python

    from bonobo import Graph, ThreadPoolExecutorStrategy

    # Represent our data processor as a simple directed graph of callables.
    graph = Graph()
    graph.add_chain(
        ('foo', 'bar', 'baz'),
        str.upper,
        print,
    )

    # Use a thread pool.
    executor = ThreadPoolExecutorStrategy()

    # Run the thing.
    executor.execute(graph)

We also switched our generator for a tuple, **Bonobo** will wrap it as a generator itself if it's not callable but
iterable.

The shorthand version with builtins would look like this:

.. code-block:: python

    from bonobo import run

    run(
        ('foo', 'bar', 'baz'),
        str.upper,
        print,
    )

Both methods are strictly equivalent (see :func:`bonobo.run`). When in doubt, prefer the shorter version.

Takeaways
:::::::::

① The :class:`bonobo.Graph` class is used to represent a data-processing pipeline.

It can represent simple list-like linear graphs, like here, but it can also represent much more complex graphs, with
branches and cycles.

This is what the graph we defined looks like:

.. graphviz::

    digraph {
        rankdir = LR;
        "iter(['foo', 'bar', 'baz'])" -> "str.upper" -> "print";
    }


② `Components` are simple python callables. Whatever can be called can be used as a `component`. Callables can
either `return` or `yield` data to send it to the next step. Regular functions (using `return`) should be prefered if
each call is guaranteed to return exactly one result, while generators (using `yield`) should be prefered if the
number of output lines for a given input varies.

③ The `graph` is then executed using an `ExecutionStrategy`. In this tutorial, we'll only use
:class:`bonobo.ThreadPoolExecutorStrategy`, which use an underlying `concurrent.futures.ThreadPoolExecutor` to
schedule calls in a pool of threads, but basically this strategy is what determines the actual behaviour of execution.

④ Before actually executing the `components`, the `ExecutorStrategy` instance will wrap each component in a `context`,
whose responsibility is to hold the state, to keep the `components` stateless. We'll expand on this later.

Concepts and definitions
::::::::::::::::::::::::

* Component
* Graph
* Executor

.. todo:: Definitions, and substitute vague terms in the page by the exact term defined here


Next
::::

You now know all the basic concepts necessary to build (batch-like) data processors.

If you're confident with this part, let's get to a more real world example, using files and nice console output:
:doc:`basics2`

