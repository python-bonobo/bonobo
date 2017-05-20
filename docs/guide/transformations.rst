Transformations
===============

Here is some guidelines on how to write transformations, to avoid the convention-jungle that could happen without
a few rules.


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

If you're naming something which is configurable, that will need to be instanciated or called to obtain something that
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
    )


It does not allow any configuration, but if it's an option, prefer it as it's simpler to write.


Class based transformations
:::::::::::::::::::::::::::

A lot of logic is a bit more complex, and you'll want to use classes to define some of your transformations.

The :class:`bonobo.config.Configurable` class gives you a few toys to write configurable transformations.

Options
-------

.. autoclass:: bonobo.config.Option

Services
--------

.. autoclass:: bonobo.config.Service

Method
------

.. autoclass:: bonobo.config.Method


