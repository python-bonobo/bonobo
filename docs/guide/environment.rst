Environment Variables
=====================

Best practice holds that variables should be passed to graphs via environment variables.
Doing this is important for keeping sensitive data out of the code - such as an
API token or username and password used to access a database. Not only is this
approach more secure, it also makes graphs more flexible by allowing adjustments
for a variety of environments and contexts. Importantly, environment variables
are also the means by-which arguments can be passed to graphs.


Passing / Setting Environment Variables
:::::::::::::::::::::::::::::::::::::::

Setting environment variables for your graphs to use can be done in a variety of ways and which one used can vary
based-upon context. Perhaps the most immediate and simple way to set/override a variable for a given graph is 
simply to use the optional ``--env`` argument when running bonobo from the shell (bash, command prompt, etc). 
``--env`` (or ``-e`` for short) should then be followed by the variable name and value using the
syntax ``VAR_NAME=VAR_VALUE``. Multiple environment variables can be passed by using multiple ``--env`` / ``-e`` flags
(i.e. ``bonobo run --env FIZZ=buzz ...`` and ``bonobo run --env FIZZ=buzz --env Foo=bar ...``). Additionally, in bash
you can also set environment variables by listing those you wish to set before the `bonobo run` command with space
separating the key-value pairs (i.e. ``FIZZ=buzz bonobo run ...`` or ``FIZZ=buzz FOO=bar bonobo run ...``).

The Examples below demonstrate setting one or multiple variables using both of these methods:

.. code-block:: bash

    # Using one environment variable via --env flag:
    bonobo run csvsanitizer --env SECRET_TOKEN=secret123

    # Using multiple environment variables via -e (env) flag:
    bonobo run csvsanitizer -e SRC_FILE=inventory.txt -e DST_FILE=inventory_processed.csv
    
    # Using one environment variable inline (bash only):
    SECRET_TOKEN=secret123 bonobo run csvsanitizer

    # Using multiple environment variables inline (bash only):
    SRC_FILE=inventory.txt DST_FILE=inventory_processed.csv bonobo run csvsanitizer
    
*Though not-yet implemented, the bonobo roadmap includes implementing environment / .env files as well.*

Accessing Environment Variables from within the Graph Context
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Environment variables, whether set globally or only for the scope of the graph,
can be can be accessed using any of the normal means. It is important to note
that whether set globally for the system or just for the graph context,
environment variables are accessed by bonobo in the same way. In the example
below the database user and password are accessed via the ``os`` module's ``getenv``
function and used to get data from the database.

.. code-block:: python

    import os

    import bonobo
    from bonobo.config import use


    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')


    @use('database')
    def extract(database):
        with database.connect(DB_USER, DB_PASS) as conn:
            yield from conn.query_all()


    graph = bonobo.Graph(
        extract,
        bonobo.PrettyPrinter(),
    )

