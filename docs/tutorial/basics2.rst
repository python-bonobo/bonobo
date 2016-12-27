First steps - Working with files
================================

Bonobo would not be of any use if the aim was to uppercase small lists of strings. In fact, Bonobo should not be used
if you don't expect any gain from parralelization of tasks.

Let's take the following graph as an example:

.. graphviz::

    digraph {
        rankdir = LR;
        "A" -> "B" -> "C";
    }

The execution strategy does a bit of under the scene work, wrapping every component in a thread (assuming you're using
the :class:`bonobo.ThreadPoolExecutorStrategy`), which allows to start running `B` as soon as `A` yielded the first line
of data, and `C` as soon as `B` yielded the first line of data, even if `A` or `B` still have data to yield.

The great thing is that you generally don't have to think about it. Just be aware that your components will be run in
parralel, and don't worry too much about blocking components, as they won't block their siblings.

That being said, let's try to write a more real-world like transformation.

Reading a file
::::::::::::::

There are a few component builders available in **Bonobo** that let you read files. You should at least know about the following:

* :class:`bonobo.FileReader` (aliased as :func:`bonobo.from_file`)
* :class:`bonobo.JsonFileReader` (aliased as :func:`bonobo.from_json`)
* :class:`bonobo.CsvFileReader` (aliased as :func:`bonobo.from_csv`)

Reading a file is as simple as using one of those, and for the example, we'll use a text file that was generated using
Bonobo from the "liste-des-cafes-a-un-euro" dataset made available by Mairie de Paris under the Open Database
License (ODbL). You can `explore the original dataset <https://opendata.paris.fr/explore/dataset/liste-des-cafes-a-un-euro/information/>`_.
You'll need the example dataset, available in **Bonobo**'s repository.

.. code-block:: python

    from bonobo import FileReader, run

    run(
        FileReader('examples/datasets/cheap_coffeeshops_in_paris.txt'),
        print,
    )
