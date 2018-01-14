Working with Django
===================

|bonobo| provides a lightweight integration with django, to allow to write management commands using |bonobo| graphs.

Management Command
::::::::::::::::::

To write a management command with |bonobo|, just extend the :class:`bonobo.contrib.django.ETLCommand` class and
override the `get_graph()` method.

Example:

.. code-block:: python

    import bonobo
    from bonobo.contrib.django import ETLCommand

    class Command(ETLCommand):
        def get_graph(self, **options):
            graph = bonobo.Graph()
            graph.add_chain(...)
            return graph

You can also override the `get_services()` method.

One common recipe to do so is to import it from somewhere else and override it as a :obj:`staticmethod`:

.. code-block:: python

    import bonobo
    from bonobo.contrib.django import ETLCommand

    from myproject.services import get_services

    class Command(ETLCommand):
        get_services = staticmethod(get_services)

        def get_graph(...):
            ...

Source code
:::::::::::

https://github.com/python-bonobo/bonobo/tree/master/bonobo/contrib/django

Reference
:::::::::

.. automodule:: bonobo.contrib.django
    :members:
    :undoc-members:
    :show-inheritance:
