Part 1: Let's get started!
==========================

To get started with |bonobo|, you need to install it in a working python 3.5+ environment (you should use a
`virtualenv <https://virtualenv.pypa.io/>`_).

.. code-block:: shell-session

    $ pip install bonobo

Check that the installation worked, and that you're using a version that matches this tutorial (written for bonobo
|longversion|).

.. code-block:: shell-session

    $ bonobo version

See :doc:`/install` for more options.


Create an ETL job
:::::::::::::::::

Since Bonobo 0.6, it's easy to bootstrap a simple ETL job using just one file.

We'll start here, and the later stages of the tutorial will guide you toward refactoring this to a python package.

.. code-block:: shell-session

    $ bonobo init tutorial.py

This will create a simple job in a `tutorial.py` file. Let's run it:

.. code-block:: shell-session

    $ python tutorial.py
    Hello
    World
     - extract in=1 out=2 [done]
     - transform in=2 out=2 [done]
     - load in=2 [done]

Congratulations! You just ran your first |bonobo| ETL job.


Inspect your graph
::::::::::::::::::

The basic building blocks of |bonobo| are **transformations** and **graphs**.

**Transformations** are simple python callables (like functions) that handle a transformation step for a line of data.

**Graphs** are a set of transformations, with directional links between them to define the data-flow that will happen
at runtime.

To inspect the graph of your first transformation:

.. note::

    You must `install the graphviz software first <https://www.graphviz.org/download/>`_. It is _not_ the python's graphviz
    package, you must install it using your system's package manager (apt, brew, ...).
    
    For Windows users: you might need to add an entry to the Path environment variable for the `dot` command to be             recognized

.. code-block:: shell-session

    $ bonobo inspect --graph tutorial.py | dot -Tpng -o tutorial.png

Open the generated `tutorial.png` file to have a quick look at the graph.

.. graphviz::

    digraph {
      rankdir = LR;
      "BEGIN" [shape="point"];
      "BEGIN" -> {0 [label="extract"]};
      {0 [label="extract"]} -> {1 [label="transform"]};
      {1 [label="transform"]} -> {2 [label="load"]};
    }

You can easily understand here the structure of your graph. For such a simple graph, it's pretty much useless, but as
you'll write more complex transformations, it will be helpful.


Read the Code
:::::::::::::

Before we write our own job, let's look at the code we have in `tutorial.py`.


Import
------

.. code-block:: python

    import bonobo


The highest level APIs of |bonobo| are all contained within the top level **bonobo** namespace.

If you're a beginner with the library, stick to using only those APIs (they also are the most stable APIs).

If you're an advanced user (and you'll be one quite soon), you can safely use second level APIs.

The third level APIs are considered private, and you should not use them unless you're hacking on |bonobo| directly.


Extract
-------

.. code-block:: python

    def extract():
        yield 'hello'
        yield 'world'

This is a first transformation, written as a `python generator <https://docs.python.org/3/glossary.html#term-generator>`_, that will send some strings, one after the other, to its
output.

Transformations that take no input and yields a variable number of outputs are usually called **extractors**. You'll
encounter a few different types, either purely generating the data (like here), using an external service (a
database, for example) or using some filesystem (which is considered an external service too).

Extractors do not need to have its input connected to anything, and will be called exactly once when the graph is
executed.


Transform
---------

.. code-block:: python

    def transform(*args):
        yield tuple(
            map(str.title, args)
        )

This is a second transformation. It will get called a bunch of times, once for each input row it gets, and apply some
logic on the input to generate the output.

This is the most **generic** case. For each input row, you can generate zero, one or many lines of output for each line
of input.


Load
----

.. code-block:: python

    def load(*args):
        print(*args)

This is the third and last transformation in our "hello world" example. It will apply some logic to each row, and have
absolutely no output.

Transformations that take input and yields nothing are also called **loaders**. Like extractors, you'll encounter
different types, to work with various external systems.

Please note that as a convenience mean and because the cost is marginal, most builtin `loaders` will send their
inputs to their output unmodified, so you can easily chain more than one loader, or apply more transformations after a
given loader.


Graph Factory
-------------

.. code-block:: python

    def get_graph(**options):
        graph = bonobo.Graph()
        graph.add_chain(extract, transform, load)
        return graph

All our transformations were defined above, but nothing ties them together, for now.

This "graph factory" function is in charge of the creation and configuration of a :class:`bonobo.Graph` instance, that
will be executed later.

By no mean is |bonobo| limited to simple graphs like this one. You can add as many chains as you want, and each chain
can contain as many nodes as you want.


Services Factory
----------------

.. code-block:: python

    def get_services(**options):
        return {}

This is the "services factory", that we'll use later to connect to external systems. Let's skip this one, for now.

(we'll dive into this topic in :doc:`4-services`)


Main Block
----------

.. code-block:: python

    if __name__ == '__main__':
        parser = bonobo.get_argument_parser()
        with bonobo.parse_args(parser) as options:
            bonobo.run(
                get_graph(**options),
                services=get_services(**options)
            )
            
Here, the real thing happens.

Without diving into too much details for now, using the :func:`bonobo.parse_args` context manager will allow our job to
be configurable, later, and although we don't really need it right now, it does not harm neither.

.. note::

    This is intended to run in a console terminal. If you're working in a jupyter notebook, you need to adapt the thing to
    avoid trying to parse arguments, or you'll get into trouble.

Reading the output
::::::::::::::::::

Let's run this job once again:

.. code-block:: shell-session

    $ python tutorial.py
    Hello
    World
     - extract in=1 out=2 [done]
     - transform in=2 out=2 [done]
     - load in=2 [done]

The console output contains two things.

* First, it contains the real output of your job (what was :func:`print`-ed to `sys.stdout`).
* Second, it displays the execution status (on `sys.stderr`). Each line contains a "status" character, the node name,
  numbers and a human readable status. This status will evolve in real time, and allows to understand a job's progress
  while it's running.

  * Status character:

    * “ ” means that the node was not yet started.
    * “`-`” means that the node finished its execution.
    * “`+`” means that the node is currently running.
    * “`!`” means that the node had problems running.

  * Numerical statistics:

    * “`in=...`” shows the input lines count, also known as the amount of calls to your transformation.
    * “`out=...`” shows the output lines count.
    * “`read=...`” shows the count of reads applied to an external system, if the transformation supports it.
    * “`write=...`” shows the count of writes applied to an external system, if the transformation supports it.
    * “`err=...`” shows the count of exceptions that happened while running the transformation. Note that exception will abort
      a call, but the execution will move to the next row.


However, if you run the tutorial.py it happens too fast and you can't see the status change. Let's add some delays to your code.

At the top of tutorial.py add a new import and add some delays to the 3 stages:

.. code-block:: python

    import time

    def extract():
        """Placeholder, change, rename, remove... """
        time.sleep(5)
        yield 'hello'
        time.sleep(5)
        yield 'world'


    def transform(*args):
        """Placeholder, change, rename, remove... """
        time.sleep(5)
        yield tuple(
            map(str.title, args)
        )


    def load(*args):
        """Placeholder, change, rename, remove... """
        time.sleep(5)
        print(*args)

Now run tutorial.py again, and you can see the status change during the process.

Wrap up
:::::::

That's all for this first step.

You now know:

* How to create a new job (using a single file).
* How to inspect the content of a job.
* What should go in a job file.
* How to execute a job file.
* How to read the console output.

It's now time to jump to :doc:`2-jobs`.
