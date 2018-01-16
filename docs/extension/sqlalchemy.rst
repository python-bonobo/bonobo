.. currentmodule:: bonobo_sqlalchemy

Working with SQLAlchemy
=======================

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

First, you'll need a database connection (:obj:`sqlalchemy.engine.Engine` instance), that must be provided as a service.

.. code-block:: python

    import sqlalchemy

    def get_services():
        return {
            'sqlalchemy.engine': sqlalchemy.create_engine(...)
        }

The `sqlalchemy.engine` name is the default name used by the provided transformations, but you can override it (for
example if you need more than one connection) and specify the service name using `engine='myengine'` while building your
transformations.

There are two transformation classes provided by this extension.

One reader, one writer.

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

:mod:`bonobo_sqlalchemy`
------------------------

.. automodule:: bonobo_sqlalchemy

Source code
:::::::::::

https://github.com/python-bonobo/bonobo-sqlalchemy

