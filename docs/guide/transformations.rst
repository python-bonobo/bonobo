Transformations
===============

Transformations are the smallest building blocks in Bonobo ETL.

They are written using standard python callables (or iterables, if you're writing transformations that have no input,
a.k.a extractors).

Definitions
:::::::::::

Transformation

    The base building block of Bonobo, anything you would insert in a graph as a node. Mostly, a callable or an iterable.

Extractor

    Special case transformation that use no input. It will be only called once, and its purpose is to generate data,
    either by itself or by requesting it from an external service.

Loader

    Special case transformation that feed an external service with data. For convenience, it can also yield the data but
    a "pure" loader would have no output (although yielding things should have no bad side effect).

Callable

    Anything one can call, in python. Can be a function, a python builtin, or anything that implements `__call__`

Iterable

    Something we can iterate on, in python, so basically anything you'd be able to use in a `for` loop.


Function based transformations
::::::::::::::::::::::::::::::

The most basic transformations are function-based. Which means that you define a function, and it will be used directly
in a graph.

.. code-block:: python

    def get_representation(row):
        return repr(row)

    graph = bonobo.Graph(
        [...],
        get_representation,
        [...],
    )


It does not allow any configuration, but if it's an option, prefer it as it's simpler to write.


Class based transformations
:::::::::::::::::::::::::::

For less basic use cases, you'll want to use classes to define some of your transformations. It's also a better choice
to build reusable blocks, as you'll be able to create parametrizable transformations that the end user will be able to
configure at the last minute.


Configurable
------------

.. autoclass:: bonobo.config.Configurable

Options
-------

.. autoclass:: bonobo.config.Option

Services
--------

.. autoclass:: bonobo.config.Service

Methods
-------

.. autoclass:: bonobo.config.Method

ContextProcessors
-----------------

.. autoclass:: bonobo.config.ContextProcessor


Naming conventions
::::::::::::::::::

The naming convention used is the following.

If you're naming something which is an actual transformation, that can be used directly as a graph node, then use
underscores and lowercase names:

.. code-block:: python

    # instance of a class based transformation
    filter = Filter(...)

    # function based transformation
    def uppercase(s: str) -> str:
        return s.upper()

If you're naming something which is configurable, that will need to be instantiated or called to obtain something that
can be used as a graph node, then use camelcase names:

.. code-block:: python

    # configurable
    class ChangeCase(Configurable):
        modifier = Option(default='upper')
        def call(self, s: str) -> str:
            return getattr(s, self.modifier)()

    # transformation factory
    def Apply(method):
        @functools.wraps(method)
        def apply(s: str) -> str:
            return method(s)
        return apply

    # result is a graph node candidate
    upper = Apply(str.upper)


Testing
:::::::

As Bonobo use plain old python objects as transformations, it's very easy to unit test your transformations using your
favourite testing framework. We're using pytest internally for Bonobo, but it's up to you to use the one you prefer.

If you want to test a transformation with the surrounding context provided (for example, service instances injected, and
context processors applied), you can use :class:`bonobo.execution.NodeExecutionContext` as a context processor and have
bonobo send the data to your transformation.


.. code-block:: python

    from bonobo.constants import BEGIN, END
    from bonobo.execution import NodeExecutionContext

    with NodeExecutionContext(
        JsonWriter(filename), services={'fs': ...}
    ) as context:

        # Write a list of rows, including BEGIN/END control messages.
        context.write(
            BEGIN,
            Bag({'foo': 'bar'}),
            Bag({'foo': 'baz'}),
            END
        )

        # Out of the bonobo main loop, we need to call `step` explicitely.
        context.step()
        context.step()

