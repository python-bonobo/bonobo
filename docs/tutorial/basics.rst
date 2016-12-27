First steps - Basic concepts
============================

To begin with Bonobo, you should first install it:

.. code-block:: shell-session

    $ pip install bonobo

See :doc:`install` if you're looking for more options.

Let's write a first data transformation
:::::::::::::::::::::::::::::::::::::::

We'll write a simple component that just uppercase everything. In **Bonobo**, a component is a plain old python
callable, not more, not less.

.. code-block:: python

    def uppercase(x: str):
        return x.upper()

Ok, this is kind of simple, and you can even use `str.upper` directly instead of writing a wrapper. The type annotations
are not used, but can make your code much more readable (and may be used as validators in the future).

To run this, we need two more things: a generator that feeds data, and something that outputs it.

.. code-block:: python

    def generate_data():
        yield 'foo'
        yield 'bar'
        yield 'baz'

    def output(x: str):
        print(x)

That should do the job. Now, let's chain the three callables together and run them.

.. code-block:: python

    from bonobo import run

    run(generate_data, uppercase, output)

This is the simplest data transormation possible, and we run it using the `run` helper that hides the underlying object
composition necessary to actually run the callables in parralel. The more flexible, but a bit more verbose to do the
same thing would be:

.. code-block:: python

    from bonobo import Graph, ThreadPoolExecutorStrategy

    graph = Graph()
    graph.add_chain(generate_data, uppercase, output)

    executor = ThreadPoolExecutorStrategy()
    executor.execute(graph)

Depending on what you're doing, you may use the shorthand helper method, or the verbose one. Always favor the shorter,
if you don't need to tune the graph or the execution strategy.

Definitions
:::::::::::

* Graph
* Component
* Executor

.. todo:: Definitions, and substitute vague terms in the page by the exact term defined here

Summary
:::::::

Let's rewrite this using builtin functions and methods, then explain the few concepts available here:

.. code-block:: python

    from bonobo import Graph, ThreadPoolExecutorStrategy

    # Represent our data processor as a simple directed graph of callables.
    graph = Graph(
        (x for x in 'foo', 'bar', 'baz'),
        str.upper,
        print,
    )

    # Use a thread pool.
    executor = ThreadPoolExecutorStrategy()

    # Run the thing.
    executor.execute(graph)

Or the shorthand version, that you should prefer if you don't need fine tuning:

.. code-block:: python

    from bonobo import run

    run(
        iter(['foo', 'bar', 'baz']),
        str.upper,
        print,
    )

Both methods are strictly equivalent (see :func:`bonobo.run`). When in doubt, favour the shorter.

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


② Transformations are simple python callables. Whatever can be called can be used as a transformation. Callables can
either `return` or `yield` data to send it to the next step. Regular functions (using `return`) should be prefered if
each call is guaranteed to return exactly one result, while generators (using `yield`) should be prefered if the
number of output lines for a given input varies.

③ The graph is then executed using an `ExecutionStrategy`. For now, let's focus only on
:class:`bonobo.ThreadPoolExecutorStrategy`, which use an underlying `concurrent.futures.ThreadPoolExecutor` to
schedule calls in a pool of threads, but basically this strategy is what determines the actual behaviour of execution.

④ Before actually executing the callables, the `ExecutorStrategy` instance will wrap each component in a `context`,
whose responsibility is to hold the state, to keep the components stateless. We'll expand on this later.


Next
::::

You now know all the basic concepts necessary to build (batch-like) data processors.

If you're confident with this part, let's get to a more real world example, using files and nice console output.

.. todo:: link to next page
