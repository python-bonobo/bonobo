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

Lets create some tables and add some data. (You may need to edit the SQL if your database server uses a different
version of SQL.)

.. code-block:: sql

    CREATE TABLE test_in (
      id INTEGER PRIMARY KEY NOT NULL,
      text TEXT
    );

    CREATE TABLE test_out (
      id INTEGER PRIMARY KEY NOT NULL,
      text TEXT
    );

    INSERT INTO test_in (id, text) VALUES (1, 'Cat');
    INSERT INTO test_in (id, text) VALUES (2, 'Dog');


There are two transformation classes provided by this extension.

One reader, one writer.

Let's select some data:

.. code-block:: python

    import bonobo
    import bonobo_sqlalchemy

    def get_graph():
        graph = bonobo.Graph()
        graph.add_chain(
            bonobo_sqlalchemy.Select('SELECT * FROM test_in', limit=100),
            bonobo.PrettyPrinter(),
        )
        return graph

You should see:

.. code-block:: shell-session

    $ python tutorial.py
    ┌
    │ id[0] = 1
    │ text[1] = 'Cat'
    └
    ┌
    │ id[0] = 2
    │ text[1] = 'Dog'
    └
     - Select in=1 out=2 [done]
     - PrettyPrinter in=2 out=2 [done]


Now let's insert some data:

.. code-block:: python

    import bonobo
    import bonobo_sqlalchemy


    def get_graph(**options):
        graph = bonobo.Graph()
        graph.add_chain(
            bonobo_sqlalchemy.Select('SELECT * FROM test_in', limit=100),
            bonobo_sqlalchemy.InsertOrUpdate('test_out')
        )

        return graph

If you check the `test_out` table, it should now have the data.

Reference
:::::::::

:mod:`bonobo_sqlalchemy`
------------------------

.. automodule:: bonobo_sqlalchemy

Source code
:::::::::::

https://github.com/python-bonobo/bonobo-sqlalchemy

