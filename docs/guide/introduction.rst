Introduction
============

The first thing you need to understand before you use Bonobo, or not, is what it does and what it does not, so you can
understand if it could be a good fit for your use cases.

How it works?
:::::::::::::

**Bonobo** is an **Extract Transform Load** framework aimed at coders, hackers, or any other person who's at ease with
terminals and source code files.

It is a **data streaming** solution, that treat datasets as ordered collections of independant rows, allowing to process
them "first in, first out" using a set of transformations organized together in a directed graph.

Let's take a few examples:

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        END [shape="none" label="..."];
        BEGIN -> "A" -> "B" -> "C" -> "END";
    }

One of the simplest, by the book, cases, is an extractor sending to a transformation, itself sending to a loader.

Bonobo will send an "impulsion" to all transformations linked to the little black dot on the left, here `A`.
`A`'s main topic will be to extract data from somewhere (a file, an endpoint, a database...) and generate some output.
As soon as the first row of `A`'s output is available, Bonobo will start asking `B` to process it. As soon as the first
row of `B`'s output is available, Bonobo will start asking `C` to process it.

While `B` and `C` are processing, `A` continues to generate data.

This approach can be efficient, depending on your requirements, because you may rely on a lot of services that may be
long to answer or unreliable, and you don't have to handle optimizations, parallelism or retry logic by yourself.

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        END [shape="none" label="..."];
        END2 [shape="none" label="..."];
        BEGIN -> "A" -> "B" -> "END";
        "A" -> "C" -> "END2";
    }

In this case, any output row of `A`, will be **sent to both** `B` and `C` simultaneously. Again, `A` will continue its
processing while `B` and `C` are working.


.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN2 [shape="point"];
        END [shape="none" label="..."];
        BEGIN -> "A" -> "C" -> "END";
        BEGIN2 -> "B" -> "C";
    }


What is it not?
:::::::::::::::

**Bonobo** is not:

* A data science, or statistical analysis tool, which need to treat the dataset as a whole and not as a collection of
  independant rows. If this is your need, you probably want to look at `pandas <https://pandas.pydata.org/>`_.

* A workflow or scheduling solution for independant data-engineering tasks. If you're looking to manage your sets of
  data processing tasks as a whole, you probably want to look at `airflow <https://airflow.incubator.apache.org/>`_.
  Although there is no Bonobo extension yet that handles that, it does make sense to integrate Bonobo jobs in an airflow
  (or other similar tool) workflow.

* A big data solution, `as defined by wikipedia <https://en.wikipedia.org/wiki/Big_data>`_. We're aiming at "small
  scale" data processing, which can be still quite huge for humans, but not for computers. If you don't know whether or
  not this is sufficient for your needs, it probably means you're not in the "big data" land.


Where to jump next?
:::::::::::::::::::

If you did not run through it yet, we highly suggest that you go through the :doc:`tutorial </tutorial/index>` first.

Then, you can jump to the following guides, in no particuliar order:

.. toctree::
    :maxdepth: 1

    transformations
    graphs
    services
    environment
    purity


