Working with SQL Databases
==========================

.. include:: _beta.rst

Read the introduction: https://www.bonobo-project.org/with/sqlalchemy

Installation
::::::::::::

To install the extension, use the `sqlalchemy` extra:

.. code-block:: shell-session

    $ pip install bonobo[sqlalchemy]

.. note:: You can install more than one extra at a time separating the names with commas.

Overview and examples
:::::::::::::::::::::

There are two main tools provided by this extension. One reader, one writer.

Let's select some data:

.. code-block:: python

    import bonobo
    import bonobo_sqlalchemy

    def get_graph():
        graph = bonobo.Graph()
        graph.add_chain(
            bonobo_sqlalchemy.Select('SELECT * FROM example', limit=100),
            bonobo.PrettyPrinter(),
        )

And let's insert some data:

.. code-block:: python

    import bonobo
    import bonobo_sqlalchemy


    def get_graph(**options):
        graph = bonobo.Graph()
        graph.add_chain(
            ...,
            bonobo_sqlalchemy.InsertOrUpdate('example')
        )

        return graph


Reference
:::::::::

.. module:: bonobo_sqlalchemy

Select
------

.. autoclass:: Select

InsertOrUpdate
--------------

.. autoclass:: InsertOrUpdate

Source code
:::::::::::

https://github.com/python-bonobo/bonobo-sqlalchemy

