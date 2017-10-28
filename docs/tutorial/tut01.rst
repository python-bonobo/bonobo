Let's get started!
==================

To begin with Bonobo, you need to install it in a working python 3.5+ environment, and you'll also need cookiecutter
to bootstrap your project.

.. code-block:: shell-session

    $ pip install bonobo cookiecutter

See :doc:`/install` for more options.


Create an empty project
:::::::::::::::::::::::

Your ETL code will live in ETL projects, which are basically a bunch of files, including python code, that bonobo
can run.

.. code-block:: shell-session

    $ bonobo init tutorial

This will create a `tutorial` directory (`content description here <https://www.bonobo-project.org/with/cookiecutter>`_).

To run this project, use:

.. code-block:: shell-session

    $ bonobo run tutorial


Write a first transformation
::::::::::::::::::::::::::::

Open `tutorial/main.py`, and delete all the code here.

A transformation can be whatever python can call. Simplest transformations are functions and generators.

Let's write one:

.. code-block:: python

    def transform(x):
        return x.upper()

Easy.

.. note::

    This function is very similar to :func:`str.upper`, which you can use directly.

Let's write two more transformations for the "extract" and "load" steps. In this example, we'll generate the data from
scratch, and we'll use stdout to "simulate" data-persistence.

.. code-block:: python

    def extract():
        yield 'foo'
        yield 'bar'
        yield 'baz'

    def load(x):
        print(x)

Bonobo makes no difference between generators (yielding functions) and regular functions. It will, in all cases, iterate
on things returned, and a normal function will just be seen as a generator that yields only once.

.. note::

    Once again, you should use the builtin :func:`print` directly instead of this `load()` function.


Create a transformation graph
:::::::::::::::::::::::::::::

Amongst other features, Bonobo will mostly help you there with the following:

* Execute the transformations in independant threads
* Pass the outputs of one thread to other(s) thread(s) inputs.

To do this, it needs to know what data-flow you want to achieve, and you'll use a :class:`bonobo.Graph` to describe it.

.. code-block:: python

    import bonobo

    graph = bonobo.Graph(extract, transform, load)

    if __name__ == '__main__':
        bonobo.run(graph)

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "extract" -> "transform" -> "load";
    }

.. note::

    The `if __name__ == '__main__':` section is not required, unless you want to run it directly using the python
    interpreter.

    The name of the `graph` variable is arbitrary, but this variable must be global and available unconditionally.
    Do not put it in its own function or in the `if __name__ == '__main__':` section.


Execute the job
:::::::::::::::

Save `tutorial/main.py` and execute your transformation again:

.. code-block:: shell-session

    $ bonobo run tutorial

This example is available in :mod:`bonobo.examples.tutorials.tut01e01`, and you can also run it as a module:

.. code-block:: shell-session

    $ bonobo run -m bonobo.examples.tutorials.tut01e01


Rewrite it using builtins
:::::::::::::::::::::::::

There is a much simpler way to describe an equivalent graph:

.. literalinclude:: ../../bonobo/examples/tutorials/tut01e02.py
    :language: python

The `extract()` generator has been replaced by a list, as Bonobo will interpret non-callable iterables as a no-input
generator.

This example is also available in :mod:`bonobo.examples.tutorials.tut01e02`, and you can also run it as a module:

.. code-block:: shell-session

    $ bonobo run -m bonobo.examples.tutorials.tut01e02

You can now jump to the next part (:doc:`tut02`), or read a small summary of concepts and definitions introduced here
below.

Takeaways
:::::::::

① The :class:`bonobo.Graph` class is used to represent a data-processing pipeline.

It can represent simple list-like linear graphs, like here, but it can also represent much more complex graphs, with
forks and joins.

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

③ The `Graph` instance, or `transformation graph` is executed using an `ExecutionStrategy`. You won't use it directly,
but :func:`bonobo.run` created an instance of :class:`bonobo.ThreadPoolExecutorStrategy` under the hood (the default
strategy). Actual behavior of an execution will depend on the strategy chosen, but the default should be fine for most
cases.

④ Before actually executing the `transformations`, the `ExecutorStrategy` instance will wrap each component in an
`execution context`, whose responsibility is to hold the state of the transformation. It enables to keep the
`transformations` stateless, while allowing to add an external state if required. We'll expand on this later.

Concepts and definitions
::::::::::::::::::::::::

* **Transformation**: a callable that takes input (as call parameters) and returns output(s), either as its return value or
  by yielding values (a.k.a returning a generator).

* **Transformation graph (or Graph)**: a set of transformations tied together in a :class:`bonobo.Graph` instance, which is
  a directed acyclic graph (or DAG).

* **Node**: a graph element, most probably a transformation in a graph.

* **Execution strategy (or strategy)**: a way to run a transformation graph. It's responsibility is mainly to parallelize
  (or not) the transformations, on one or more process and/or computer, and to setup the right queuing mechanism for
  transformations' inputs and outputs.

* **Execution context (or context)**: a wrapper around a node that holds the state for it. If the node needs state, there
  are tools available in bonobo to feed it to the transformation using additional call parameters, keeping
  transformations stateless.

Next
::::

Time to jump to the second part: :doc:`tut02`.

