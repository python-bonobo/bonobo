.. currentmodule:: bonobo.contrib.django

Working with Django
===================

|bonobo| provides a lightweight integration with django, to allow to include ETL pipelines in your django management
commands.

Quick start
:::::::::::

To write a django management command that runs |bonobo| job(s), just extend :class:`ETLCommand`
instead of :class:`django.core.management.base.BaseCommand`, and override the :meth:`ETLCommand.get_graph` method:

.. code-block:: python

    import bonobo
    from bonobo.contrib.django import ETLCommand

    class Command(ETLCommand):
        def get_graph(self, **options):
            graph = bonobo.Graph()
            graph.add_chain(...)
            return graph

Services
--------

You can override :meth:`ETLCommand.get_services` to provide your service implementations.

One common recipe to do so is to import it from somewhere else and override it as a :obj:`staticmethod`:

.. code-block:: python

    import bonobo
    from bonobo.contrib.django import ETLCommand

    from myproject.services import get_services

    class Command(ETLCommand):
        get_services = staticmethod(get_services)

        def get_graph(...):
            ...


Multiple graphs
---------------

The :meth:`ETLCommand.get_graph` method can also be implemented as a generator. In this case, each element yielded must
be a graph, and each graph will be executed in order:

.. code-block:: python

    import bonobo
    from bonobo.contrib.django import ETLCommand

    class Command(ETLCommand):
        def get_graph(self, **options):
            yield bonobo.Graph(...)
            yield bonobo.Graph(...)
            yield bonobo.Graph(...)

This is especially helpful in two major cases:

* You must ensure that one job is finished before the next is run, and thus you can't add both graph's nodes in the
  same graph.
* You want to change which graph is run depending on command line arguments.


Command line arguments
----------------------

Like with regular django management commands, you can add arguments to the argument parser by overriding
:meth:`ETLCommand.add_arguments`.

The only difference with django is that the provided argument parser will already have arguments added to handle
environment.


Reference
:::::::::

:mod:`bonobo.contrib.django`
----------------------------

.. automodule:: bonobo.contrib.django

Source code
:::::::::::

https://github.com/python-bonobo/bonobo/tree/master/bonobo/contrib/django

