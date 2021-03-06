Environment Variables
=====================

Best practice holds that variables should be passed to graphs via environment variables.
Doing this is important for keeping sensitive data out of the code - such as an
API token or username and password used to access a database. Not only is this
approach more secure, it also makes graphs more flexible by allowing adjustments
for a variety of environments and contexts. Importantly, environment variables
are also the means by-which arguments can be passed to graphs.

.. note::

    This document is about using your own settings and configuration values. If you're looking for bonobo's builtin
    settings, also configurable using environment variables, please check :doc:`/reference/settings`.

Passing / Setting Environment Variables
:::::::::::::::::::::::::::::::::::::::

Setting environment variables for your graphs to use can be done in a variety of ways and which one used can vary
based-upon context. Perhaps the most immediate and simple way to set/override a variable for a given graph is 
simply to use the optional ``--env`` argument when running bonobo from the shell (bash, command prompt, etc). 
``--env`` (or ``-e`` for short) should then be followed by the variable name and value using the
syntax ``VAR_NAME=VAR_VALUE``. Multiple environment variables can be passed by using multiple ``--env`` / ``-e`` flags
(i.e. ``bonobo run --env FIZZ=buzz ...`` and ``bonobo run --env FIZZ=buzz --env Foo=bar ...``). Additionally, in bash
you can also set environment variables by listing those you wish to set before the `bonobo run` command with space
separating the key-value pairs (i.e. ``FIZZ=buzz bonobo run ...`` or ``FIZZ=buzz FOO=bar bonobo run ...``). Additionally,
bonobo is able to pull environment variables from local '.env' files rather than having to pass each key-value pair
individually at runtime. Importantly, a strict 'order of priority' is followed when setting environment variables so
it is advisable to read and understand the order listed below to prevent


The order of priority is from lower to higher with the higher "winning" if set:

    1. default values
            ``os.getenv("VARNAME", default_value)``
            The user/writer/creator of the graph is responsible for setting these.

    2. ``--default-env-file`` values
            Specify file to read default env values from. Each env var in the file is used if the var isn't already a corresponding value set at the system environment (system environment vars not overwritten).

    3. ``--default-env`` values
            Works like #2 but the default ``NAME=var`` are passed individually, with one ``key=value`` pair for each ``--default-env`` flag rather than gathered from a specified file.

    4. system environment values
            Env vars already set at the system level. It is worth noting that passed env vars via ``NAME=value bonobo run ...`` falls here in the order of priority.

    5. ``--env-file`` values
            Env vars specified here are set like those in #2 albeit that these values have priority over those set at the system level.

    6. ``--env`` values
            Env vars set using the ``--env`` / ``-e`` flag work like #3 but take priority over all other env vars.



Examples
::::::::

The Examples below demonstrate setting one or multiple variables using both of these methods:

.. code-block:: bash

    # Using one environment variable via a --env or --defualt-env flag:
    bonobo run csvsanitizer --env SECRET_TOKEN=secret123
    bonobo run csvsanitizer --defaul-env SECRET_TOKEN=secret123

    # Using multiple environment variables via -e (env) and --default-env flags:
    bonobo run csvsanitizer -e SRC_FILE=inventory.txt -e DST_FILE=inventory_processed.csv
    bonobo run csvsanitizer --default-env SRC_FILE=inventory.txt --default-env DST_FILE=inventory_processed.csv

    # Using one environment variable inline (bash-like shells only):
    SECRET_TOKEN=secret123 bonobo run csvsanitizer

    # Using multiple environment variables inline (bash-like shells only):
    SRC_FILE=inventory.txt DST_FILE=inventory_processed.csv bonobo run csvsanitizer

    # Using an env file for default env values:
    bonobo run csvsanitizer --default-env-file .env

    # Using an env file for env values:
    bonobo run csvsanitizer --env-file '.env.private'


ENV File Structure
::::::::::::::::::

The file structure for env files is incredibly simple. The only text in the file
should be `NAME=value` pairs with one pair per line like the below.

.. code-block:: text

    # .env

    DB_USER='bonobo'
    DB_PASS='cicero'


Accessing Environment Variables from within the Graph Context
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Environment variables, whether set globally or only for the scope of the graph,
can be accessed using any of the normal means. It is important to note
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


.. include:: _next.rst
