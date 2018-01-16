Services and dependencies
=========================

You'll want to use external systems within your transformations, including databases, HTTP APIs, other web services,
filesystems, etc.

Hardcoding those services is a good first step, but as your codebase grows, this approach will show its limits rather quickly.

* Hardcoded and tightly linked dependencies make your transformations hard to test, and hard to reuse.
* Processing data on your laptop is great, but being able to do it on different target systems (or stages), in different
  environments is more realistic. You'll want to configure a different database on a staging environment,
  pre-production environment, or production system. Maybe you have similar systems for different clients and want to select
  the system at runtime, etc.

.. warning::

    This document is currently reviewed to check for correctness.


Definition of service dependencies
::::::::::::::::::::::::::::::::::

To solve this problem, we introduce a lightweight dependency injection system. It allows to define **named dependencies** in
your transformations and provide an implementation at runtime.

For function-based transformations, you can use the :func:`bonobo.config.use` decorator to mark the dependencies. You'll
still be able to call it manually, providing the implementation yourself, but in a bonobo execution context, it will
be resolve and injected automatically, as long as you provided an implementation to the executor (more on that below).

.. code-block:: python

    from bonobo.config import use

    @use('orders_database')
    def select_all(database):
        yield from database.query('SELECT * FROM foo;')

For class based transformations, you can use :class:`bonobo.config.Service`, a special descriptor (and subclass of
:class:`bonobo.config.Option`) that will hold the service names and act as a marker for runtime resolution of service
instances.

.. code-block:: python

    from bonobo.config import Configurable, Service

    class JoinDatabaseCategories(Configurable):
        database = Service('orders_database')

        def __call__(self, database, row):
            return {
                **row,
                'category': database.get_category_name_for_sku(row['sku'])
            }

Both of the above code samples tell bonobo that your transformation expects a service called "orders_database", which will be
injected to your calls under the parameter name "database".

Providing implementations at run-time
-------------------------------------

Bonobo expects you to provide a dictionary of all service implementations required by your graph.

.. code-block:: python

    import bonobo

    graph = bonobo.graph(...)

    def get_services():
        return {
            'orders_database': my_database_service,
        }
    
    if __name__ == '__main__':
        bonobo.run(graph, services=get_services())


.. note::

    A dictionary, or dictionary-like, "services" named argument can be passed to the :func:`bonobo.run` API method.
    The "dictionary-like" part is the real keyword here. Bonobo is not a DIC library, and won't become one. So the
    implementation provided is pretty basic and feature-less. You can use much more involved libraries instead of
    the provided stub and, as long as it implements a dictionary-like interface, the system will use it.

The command line interface will look for services in two different places:

* A `get_services()` function present at the same level of your graph definition.
* A `get_services()` function in a `_services.py` file in the same directory as your graph's file, allowing to reuse the
  same service implementations for more than one graph.

Solving concurrency problems
----------------------------

If a service cannot be used by more than one thread at a time, either because it's just not threadsafe, or because
it requires to carefully order the calls made (apis that includes nonces, or work on results returned by previous
calls are usually good candidates), you can use the :class:`bonobo.config.Exclusive` context processor to lock the
use of a dependency for the time of the context manager (`with` statement)

.. code-block:: python

    from bonobo.config import Exclusive

    def t1(api):
        with Exclusive(api):
            api.first_call()
            api.second_call()
            # ... etc
            api.last_call()



Read more
:::::::::

* See https://github.com/hartym/bonobo-sqlalchemy/blob/work-in-progress/bonobo_sqlalchemy/writers.py#L19 for example usage (work in progress).

.. include:: _next.rst
