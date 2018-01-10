Working with files
==================

.. include:: _outdated_note.rst

Bonobo would be pointless if the aim was just to uppercase small lists of strings.

In fact, Bonobo should not be used if you don't expect any gain from parallelization/distribution of tasks.

Some background...
::::::::::::::::::

Let's take the following graph:

.. graphviz::

    digraph {
        rankdir = LR;
        BEGIN [shape="point"];
        BEGIN -> "A" -> "B" -> "C";
        "B" -> "D";
    }

When run, the execution strategy wraps every component in a thread (assuming you're using the default
:class:`bonobo.strategies.ThreadPoolExecutorStrategy`).

Bonobo will send each line of data in the input node's thread (here, `A`). Now, each time `A` *yields* or *returns*
something, it will be pushed on `B` input :class:`queue.Queue`, and will be consumed by `B`'s thread. Meanwhile, `A`
will continue to run, if it's not done.

When there is more than one node linked as the output of a node (for example, with `B`, `C`, and `D`), the same thing
happens except that each result coming out of `B` will be sent to both on `C` and `D` input :class:`queue.Queue`.

One thing to keep in mind here is that as the objects are passed from thread to thread, you need to write "pure"
transformations (see :doc:`/guide/purity`).

You generally don't have to think about it. Just be aware that your nodes will run in parallel, and don't worry
too much about nodes running blocking operations, as they will run in parallel. As soon as a line of output is ready,
the next nodes will start consuming it.

That being said, let's manipulate some files.

Reading a file
::::::::::::::

There are a few component builders available in **Bonobo** that let you read from (or write to) files.

All readers work the same way. They need a filesystem to work with, and open a "path" they will read from.

* :class:`bonobo.CsvReader`
* :class:`bonobo.FileReader`
* :class:`bonobo.JsonReader`
* :class:`bonobo.PickleReader`

We'll use a text file that was generated using Bonobo from the "liste-des-cafes-a-un-euro" dataset made available by
Mairie de Paris under the Open Database License (ODbL). You can `explore the original dataset
<https://opendata.paris.fr/explore/dataset/liste-des-cafes-a-un-euro/information/>`_.

You'll need the `"coffeeshops.txt" example dataset <https://github.com/python-bonobo/bonobo/blob/master/bonobo/examples/datasets/coffeeshops.txt>`_,
available in **Bonobo**'s repository:

.. code-block:: shell-session

    $ curl https://raw.githubusercontent.com/python-bonobo/bonobo/master/bonobo/examples/datasets/coffeeshops.txt > `python3 -c 'import bonobo; print(bonobo.get_examples_path("datasets/coffeeshops.txt"))'`

.. note::

    The "example dataset download" step will be easier in the future.

    https://github.com/python-bonobo/bonobo/issues/134

.. literalinclude:: ../../bonobo/examples/tutorials/tut02e01_read.py
    :language: python

You can also run this example as a module (but you'll still need the dataset...):

.. code-block:: shell-session

    $ bonobo run -m bonobo.examples.tutorials.tut02e01_read

.. note::

    Don't focus too much on the `get_services()` function for now. It is required, with this exact name, but we'll get
    into that in a few minutes.

Writing to files
::::::::::::::::

Let's split this file's each lines on the first comma and store a json file mapping coffee names to their addresses.

Here are, like the readers, the classes available to write files

* :class:`bonobo.CsvWriter`
* :class:`bonobo.FileWriter`
* :class:`bonobo.JsonWriter`
* :class:`bonobo.PickleWriter`

Let's write a first implementation:

.. literalinclude:: ../../bonobo/examples/tutorials/tut02e02_write.py
    :language: python

(run it with :code:`bonobo run -m bonobo.examples.tutorials.tut02e02_write` or :code:`bonobo run myfile.py`)

If you read the output file, you'll see it misses the "map" part of the problem.

Let's extend :class:`bonobo.io.JsonWriter` to finish the job:

.. literalinclude:: ../../bonobo/examples/tutorials/tut02e03_writeasmap.py
    :language: python

(run it with :code:`bonobo run -m bonobo.examples.tutorials.tut02e03_writeasmap` or :code:`bonobo run myfile.py`)

It should produce a nice map.

We favored a bit hackish solution here instead of constructing a map in python then passing the whole to
:func:`json.dumps` because we want to work with streams, if you have to construct the whole data structure in python,
you'll loose a lot of bonobo's benefits.

Next
::::

Time to write some more advanced transformations, with service dependencies: :doc:`tut03`.
