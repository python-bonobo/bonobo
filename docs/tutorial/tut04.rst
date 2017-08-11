Working with databases
======================

Databases (and especially SQL databases here) are not the focus of Bonobo, thus support for it is not (and will never
be) included in the main package. Instead, working with databases is done using third party, well maintained and
specialized packages, like SQLAlchemy, or other database access libraries from the python cheese shop.

.. note::

    SQLAlchemy extension is not yet complete. Things may be not optimal, and some APIs will change. You can still try,
    of course.

    Consider the following document as a "preview" (yes, it should work, yes it may break in the future).

    Also, note that for early development stages, we explicitely support only PostreSQL, although it may work well
    with `any other database supported by SQLAlchemy <http://docs.sqlalchemy.org/en/latest/core/engines.html#supported-databases>`_.

First, read https://www.bonobo-project.org/with/sqlalchemy for instructions on how to install. You **do need** the
bleeding edge version of `bonobo` and `bonobo-sqlalchemy` to make this work.

Requirements
::::::::::::

Once you installed `bonobo_sqlalchemy` (read https://www.bonobo-project.org/with/sqlalchemy to use bleeding edge
version), install the following additional packages:

.. code-block:: shell-session

    $ pip install -U python-dotenv psycopg2 awesome-slugify

Those packages are not required by the extension, but `python-dotenv` will help us configure the database DSN, and
`psycopg2` is required by SQLAlchemy to connect to PostgreSQL databases. Also, we'll use a slugifier to create unique
identifiers for the database (maybe not what you'd do in the real world, but very much sufficient for example purpose).

Configure a database engine
:::::::::::::::::::::::::::

Open your `_services.py` file and replace the code:

.. code-block:: python

    import bonobo, dotenv, logging, os
    from bonobo_sqlalchemy.util import create_postgresql_engine

    dotenv.load_dotenv(dotenv.find_dotenv())
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    def get_services():
        return {
            'fs': bonobo.open_examples_fs('datasets'),
            'fs.output': bonobo.open_fs(),
            'sqlalchemy.engine': create_postgresql_engine(**{
                    'name': 'tutorial',
                    'user': 'tutorial',
                    'pass': 'tutorial',
                })
        }

The `create_postgresql_engine` is a tiny function building the DSN from reasonable defaults, that you can override
either by providing kwargs, or with system environment variables. If you want to override something, open the `.env`
file and add values for one or more of `POSTGRES_NAME`, `POSTGRES_USER`, 'POSTGRES_PASS`, `POSTGRES_HOST`,
`POSTGRES_PORT`. Please note that kwargs always have precedence on environment, but that you should prefer using
environment variables for anything that is not immutable from one platform to another.

Add database operation to the graph
:::::::::::::::::::::::::::::::::::

Let's create a `tutorial/pgdb.py` job:

.. code-block:: python

    import bonobo
    import bonobo_sqlalchemy

    from bonobo.examples.tutorials.tut02e03_writeasmap import graph, split_one_to_map

    graph = graph.copy()
    graph.add_chain(
        bonobo_sqlalchemy.InsertOrUpdate('coffeeshops'),
        _input=split_one_to_map
    )

Notes here:

* We use the code from :doc:`tut02`, which is bundled with bonobo in the `bonobo.examples.tutorials` package.
* We "fork" the graph, by creating a copy and appending a new "chain", starting at a point that exists in the other
  graph.
* We use :class:`bonobo_sqlalchemy.InsertOrUpdate` (which role, in case it is not obvious, is to create database rows if
  they do not exist yet, or update the existing row, based on a "discriminant" criteria (by default, "id")).

If we run this transformation (with `bonobo run tutorial/pgdb.py`), we should get an error:

.. code-block:: text

     |   File ".../lib/python3.6/site-packages/psycopg2/__init__.py", line 130, in connect
     |     conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
     | sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL:  database "tutorial" does not exist
     |
     |
     | The above exception was the direct cause of the following exception:
     |
     | Traceback (most recent call last):
     |   File ".../bonobo-devkit/bonobo/bonobo/strategies/executor.py", line 45, in _runner
     |     node_context.start()
     |   File ".../bonobo-devkit/bonobo/bonobo/execution/base.py", line 75, in start
     |     self._stack.setup(self)
     |   File ".../bonobo-devkit/bonobo/bonobo/config/processors.py", line 94, in setup
     |     _append_to_context = next(_processed)
     |   File ".../bonobo-devkit/bonobo-sqlalchemy/bonobo_sqlalchemy/writers.py", line 43, in create_connection
     |     raise UnrecoverableError('Could not create SQLAlchemy connection: {}.'.format(str(exc).replace('\n', ''))) from exc
     | bonobo.errors.UnrecoverableError: Could not create SQLAlchemy connection: (psycopg2.OperationalError) FATAL:  database "tutorial" does not exist.

The database we requested do not exist. It is not the role of bonobo to do database administration, and thus there is
no tool here to create neither the database, nor the tables we want to use.

Create database and table
:::::::::::::::::::::::::

There are however tools in `sqlalchemy` to manage tables, so we'll create the database by ourselves, and ask sqlalchemy
to create the table:

.. code-block:: shell-session

    $ psql -U postgres -h localhost

    psql (9.6.1, server 9.6.3)
    Type "help" for help.

    postgres=# CREATE ROLE tutorial WITH LOGIN PASSWORD 'tutorial';
    CREATE ROLE
    postgres=# CREATE DATABASE tutorial WITH OWNER=tutorial TEMPLATE=template0 ENCODING='utf-8';
    CREATE DATABASE

Now, let's use a little trick and add this section to `pgdb.py`:

.. code-block:: python

    import sys
    from sqlalchemy import Table, Column, String, Integer, MetaData

    def main():
        from bonobo.commands.run import get_default_services
        services = get_default_services(__file__)
        if len(sys.argv) == 1:
            return bonobo.run(graph, services=services)
        elif len(sys.argv) == 2 and sys.argv[1] == 'reset':
            engine = services.get('sqlalchemy.engine')
            metadata = MetaData()

            coffee_table = Table(
                'coffeeshops',
                metadata,
                Column('id', String(255), primary_key=True),
                Column('name', String(255)),
                Column('address', String(255)),
            )

            metadata.drop_all(engine)
            metadata.create_all(engine)
        else:
            raise NotImplementedError('I do not understand.')

    if __name__ == '__main__':
        main()

.. note::

    We're using private API of bonobo here, which is unsatisfactory, discouraged and may change. Some way to get the
    service dictionnary will be added to the public api in a future release of bonobo.

Now run:

.. code-block:: python

    $ python tutorial/pgdb.py reset

Database and table should now exist.

Format the data
:::::::::::::::

Let's prepare our data for database, and change the `.add_chain(..)` call to do it prior to `InsertOrUpdate(...)`

.. code-block:: python

    from slugify import slugify_url

    def format_for_db(row):
        name, address = list(row.items())[0]
        return {
                'id': slugify_url(name),
                'name': name,
                'address': address,
            }

    # ...

    graph = graph.copy()
    graph.add_chain(
        format_for_db,
        bonobo_sqlalchemy.InsertOrUpdate('coffeeshops'),
        _input=split_one_to_map
    )

Run!
::::

You can now run the script (either with `bonobo run tutorial/pgdb.py` or directly with the python interpreter, as we
added a "main" section) and the dataset should be inserted in your database. If you run it again, no new rows are
created.

Note that as we forked the graph from :doc:`tut02`, the transformation also writes the data to `coffeeshops.json`, as
before.

