Basic concepts
==============

To begin with Bonobo, you need to install it in a working python 3.5+ environment:

.. code-block:: shell-session

    $ pip install bonobo

See :doc:`/install` for more options.

Let's write a first data transformation
:::::::::::::::::::::::::::::::::::::::

We'll start with the simplest transformation possible.

In **Bonobo**, a transformation is a plain old python callable, not more, not less. Let's write one that takes a string
and uppercases it.

.. code-block:: python

    def uppercase(x: str):
        return x.upper()

Pretty straightforward.

You could even use :func:`str.upper` directly instead of writing a wrapper, as a type's method (unbound) will take an
instance of this type as its first parameter (what you'd call `self` in your method).

The type annotations written here are not used, but can make your code much more readable, and may very well be used as
validators in the future.

Let's write two more transformations: a generator to produce the data to be transformed, and something that outputs it,
because, yeah, feedback is cool.

.. code-block:: python

    def generate_data():
        yield 'foo'
        yield 'bar'
        yield 'baz'

    def output(x: str):
        print(x)

Once again, you could have skipped the pain of writing this and simply use an iterable to generate the data and the
builtin :func:`print` for the output, but we'll stick to writing our own transformations for now.

Let's chain the three transformations together and run the transformation graph:

.. code-block:: python

    import bonobo

    graph = bonobo.Graph(generate_data, uppercase, output)

    if __name__ == '__main__':
        bonobo.run(graph)

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "generate_data" -> "uppercase" -> "output";
    }

We use the :func:`bonobo.run` helper that hides the underlying object composition necessary to actually run the
transformations in parallel, because it's simpler.

Depending on what you're doing, you may use the shorthand helper method, or the verbose one. Always favor the shorter,
if you don't need to tune the graph or the execution strategy (see below).

Takeaways
:::::::::

① The :class:`bonobo.Graph` class is used to represent a data-processing pipeline.

It can represent simple list-like linear graphs, like here, but it can also represent much more complex graphs, with
branches and cycles.

This is what the graph we defined looks like:

.. graphviz::

    digraph {
        rankdir = LR;
        BEGIN [shape="point"];
        BEGIN -> "iter(['foo', 'bar', 'baz'])" -> "str.upper" -> "print";
    }


② `Transformations` are simple python callables. Whatever can be called can be used as a `transformation`. Callables can
either `return` or `yield` data to send it to the next step. Regular functions (using `return`) should be prefered if
each call is guaranteed to return exactly one result, while generators (using `yield`) should be prefered if the
number of output lines for a given input varies.

③ The `Graph` instance, or `transformation graph` is then executed using an `ExecutionStrategy`. You did not use it
directly in this tutorial, but :func:`bonobo.run` created an instance of :class:`bonobo.ThreadPoolExecutorStrategy`
under the hood (which is the default strategy). Actual behavior of an execution will depend on the strategy chosen, but
the default should be fine in most of the basic cases.

④ Before actually executing the `transformations`, the `ExecutorStrategy` instance will wrap each component in an
`execution context`, whose responsibility is to hold the state of the transformation. It enables to keep the
`transformations` stateless, while allowing to add an external state if required. We'll expand on this later.

Concepts and definitions
::::::::::::::::::::::::

* Transformation: a callable that takes input (as call parameters) and returns output(s), either as its return value or
  by yielding values (a.k.a returning a generator).
* Transformation graph (or Graph): a set of transformations tied together in a :class:`bonobo.Graph` instance, which is a simple
  directed acyclic graph (also refered as a DAG, sometimes).
* Node: a transformation within the context of a transformation graph. The node defines what to do with a
  transformation's output, and especially what other nodes to feed with the output.
* Execution strategy (or strategy): a way to run a transformation graph. It's responsibility is mainly to parallelize
  (or not) the transformations, on one or more process and/or computer, and to setup the right queuing mechanism for
  transformations' inputs and outputs.
* Execution context (or context): a wrapper around a node that holds the state for it. If the node needs state, there
  are tools available in bonobo to feed it to the transformation using additional call parameters, and so every
  transformation will be atomic.

Next
::::

You now know all the basic concepts necessary to build (batch-like) data processors.

If you're confident with this part, let's get to a more real world example, using files and nice console output:
:doc:`basics2`

