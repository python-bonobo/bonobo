Working with files
==================

Bonobo would be a bit useless if the aim was just to uppercase small lists of strings.

In fact, Bonobo should not be used if you don't expect any gain from parallelization/distribution of tasks.

Let's take the following graph as an example:

.. graphviz::

    digraph {
        rankdir = LR;
        BEGIN [shape="point"];
        BEGIN -> "A" -> "B" -> "C";
        "B" -> "D";
    }

The execution strategy does a bit of under the scene work, wrapping every component in a thread (assuming you're using
the :class:`bonobo.strategies.ThreadPoolExecutorStrategy`).

Bonobo will send each line of data in the input node's thread (here, `A`). Now, each time `A` *yields* or *returns*
something, it will be pushed on `B` input :class:`queue.Queue`, and will be consumed by `B`'s thread.

When there is more than one node linked as the output of a node (for example, with `B`, `C`, and `D`) , the same thing
happens except that each result coming out of `B` will be sent to both on `C` and `D` input :class:`queue.Queue`.

The great thing is that you generally don't have to think about it. Just be aware that your components will be run in
parallel (with the default strategy), and don't worry too much about blocking components, as they won't block their
siblings when run in bonobo.

That being said, let's manipulate some files.

Reading a file
::::::::::::::

There are a few component builders available in **Bonobo** that let you read from (or write to) files.

All readers work the same way. They need a filesystem to work with, and open a "path" they will read from.

* :class:`bonobo.FileReader`
* :class:`bonobo.JsonReader`
* :class:`bonobo.CsvReader`

We'll use a text file that was generated using Bonobo from the "liste-des-cafes-a-un-euro" dataset made available by
Mairie de Paris under the Open Database License (ODbL). You can `explore the original dataset
<https://opendata.paris.fr/explore/dataset/liste-des-cafes-a-un-euro/information/>`_.

You'll need the `example dataset <https://github.com/python-bonobo/bonobo/blob/0.2/bonobo/examples/datasets/coffeeshops.txt>`_,
available in **Bonobo**'s repository.

.. literalinclude:: ../../bonobo/examples/tutorials/tut02_01_read.py
    :language: python

You can run this script directly using the python interpreter:

.. code-block:: shell-session

    $ python bonobo/examples/tutorials/tut02_01_read.py

Another option is to use the bonobo cli, which allows more flexibility:

.. code-block:: shell-session

    $ bonobo run bonobo/examples/tutorials/tut02_01_read.py

Using bonobo command line has a few advantages.

It will look for one and only one :class:`bonobo.Graph` instance in the file given as argument, configure an execution
strategy, eventually plugins, and execute it. It has the benefit of allowing to tune the "artifacts" surrounding the
transformation graph on command line (verbosity, plugins ...), and it will also ease the transition to run
transformation graphs in containers, as the syntax will be the same. Of course, it is not required, and the
containerization capabilities are provided by an optional and separate python package.

It also change a bit the way you can configure service dependencies. The CLI won't run the `if __name__ == '__main__'`
block,  and thus it won't get the configured services passed to :func:`bonobo.run`. Instead, one option to configure
services is to define a `get_services()` function in a
`_services.py <https://github.com/python-bonobo/bonobo/blob/0.2/bonobo/examples/tutorials/_services.py>`_ file.

There will be more options using the CLI or environment to override things soon.

Writing to files
::::::::::::::::

Let's split this file's each lines on the first comma and store a json file mapping coffee names to their addresses.

Here are, like the readers, the classes available to write files

* :class:`bonobo.FileWriter`
* :class:`bonobo.JsonWriter`
* :class:`bonobo.CsvWriter`

Let's write a first implementation:

.. literalinclude:: ../../bonobo/examples/tutorials/tut02_02_write.py
    :language: python

You can run it and read the output file, you'll see it misses the "map" part of the question. Let's extend
:class:`bonobo.JsonWriter` to finish the job:

.. literalinclude:: ../../bonobo/examples/tutorials/tut02_03_writeasmap.py
    :language: python

You can now run it again, it should produce a nice map. We favored a bit hackish solution here instead of constructing a
map in python then passing the whole to :func:`json.dumps` because we want to work with streams, if you have to
construct the whole data structure in python, you'll loose a lot of bonobo's benefits.

