Working with files
==================

Bonobo would not be of any use if the aim was to uppercase small lists of strings. In fact, Bonobo should not be used
if you don't expect any gain from parralelization/distribution of tasks.

Let's take the following graph as an example:

.. graphviz::

    digraph {
        rankdir = LR;
        BEGIN [shape="point"];
        BEGIN -> "A" -> "B" -> "C";
    }

The execution strategy does a bit of under the scene work, wrapping every component in a thread (assuming you're using
the :class:`bonobo.ThreadPoolExecutorStrategy`), which allows to start running `B` as soon as `A` yielded the first line
of data, and `C` as soon as `B` yielded the first line of data, even if `A` or `B` still have data to yield.

The great thing is that you generally don't have to think about it. Just be aware that your components will be run in
parralel (with the default strategy), and don't worry too much about blocking components, as they won't block their
siblings when run in bonobo.

That being said, let's try to write a more real-world like transformation.

Reading a file
::::::::::::::

There are a few component builders available in **Bonobo** that let you read files. You should at least know about the
following:

* :class:`bonobo.io.FileReader`
* :class:`bonobo.io.JsonReader`
* :class:`bonobo.io.CsvReader`

Reading a file is as simple as using one of those, and for the example, we'll use a text file that was generated using
Bonobo from the "liste-des-cafes-a-un-euro" dataset made available by Mairie de Paris under the Open Database
License (ODbL). You can `explore the original dataset <https://opendata.paris.fr/explore/dataset/liste-des-cafes-a-un-euro/information/>`_.
You'll need the example dataset, available in **Bonobo**'s repository.

.. literalinclude:: ../../examples/tut02_01_read.py
    :language: python

Until then, we ran the file directly using our python interpreter, but there is other options, one of them being
`bonobo run`. This command allows to run a graph defined by a python file, and is replacing the :func:`bonobo.run`
helper. It's the exact reason why we call :func:`bonobo.run` in the `if __name__ == '__main__'` block, to only
instanciate it if it is run directly.

Using bonobo command line has a few advantages. It will look for one and only one :class:`bonobo.Graph` instance defined
in the file given as argument, configure an execution strategy, eventually plugins, and execute it. It has the benefit
of allowing to tune the "artifacts" surrounding the transformation graph on command line (verbosity, plugins ...), and
it will also ease the transition to run transformation graphs in containers, as the syntax will be the same. Of course,
it is not required, and the containerization capabilities are provided by an optional and separate python package.

.. code-block:: shell-session

    $ bonobo run examples/tut02_01_read.py





