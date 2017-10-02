Environmental Variables
=======================

Best practice holds that variables should be passed to graphs via environmental variables.
Doing this is important for keeping sensitive data out of the code - such as an
API token or username and password used to access a database. Not only is this
approach more secure, it also makes graphs more flexible by allowing adjustments
for a variety of environments and contexts. Importantly, environmental variables
are also the means by-which arguments can be passed to graphs.


Passing / Setting Environmental Variables
::::::::::::::::::::::::::::::::::::::::::::

The recommended way to set environmental variables for a given graph is simply to use
the optional ``--env`` argument when running bonobo from the shell (bash, command prompt, etc).
``--env`` (or ``-e`` for short) should then be followed by the variable name and value using the
syntax `VAR_NAME=VAR_VALUE`. Multiple environmental variables can be passed by using
multiple ``--env`` / ``-e`` flags.

Example:

.. code-block:: bash

    # Using one environmental variable:
    bonobo run csvsanitizer --env SECRET_TOKEN=secret123

    # Using multiple environmental variables:
    bonobo run csvsanitizer -e SRC_FILE=inventory.txt -e DST_FILE=inventory_processed.csv

If you're naming something which is configurable, that is will need to be instantiated or called to obtain something that
can be used as a graph node, then use camelcase names:


Accessing Environmental Variables from within the Graph Context
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Environmental variables, whether global or only for the scope of the graph,
can be can be accessed using any of the normal means. It is important to note
that whether set globally for the system or just for the graph context,
environmental variables are accessed by bonobo in the same way. In the example
below the database user and password are accessed via the ``os`` module's ``getenv``
function and used to get data from the database.

.. code-block:: python

    import os

    from bonobo import Graph, run


    def extract():
        database_user = os.getenv('DB_USER')
        database_password = os.getenv('DB_PASS')
        # ...
        # (connect to database using database_user and database_password)
        # (get data from database)
        # ...

        return database_data


    def load(database_data: dict):
        for k, v in database_data.items():
            print('{key} = {value}'.format(key=k, value=v))


    graph = Graph(extract, load)

    if __name__ == '__main__':
        run(graph)
