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


Concepts
::::::::

Whatever kind of transformation you want to use, there are a few common concepts you should know about.

Input
-----

All input is retrieved via the call arguments. Each line of input means one call to the callable provided. Arguments
will be, in order:

* Injected dependencies (database, http, filesystem, ...)
* Position based arguments
* Keyword based arguments

You'll see below how to pass each of those.

Output
------

Each callable can return/yield different things (all examples will use yield, but if there is only one output per input
line, you can also return your output row and expect the exact same behaviour).

Let's see the rules (first to match wins).

1. A flag, eventually followed by something else, marks a special behaviour. If it supports it, the remaining part of
   the output line will be interpreted using the same rules, and some flags can be combined.

   **NOT_MODIFIED**

   **NOT_MODIFIED** tells bonobo to use the input row unmodified as the output.

   *CANNOT be combined*

   Example:

   .. code-block:: python

       from bonobo import NOT_MODIFIED

       def output_will_be_same_as_input(*args, **kwargs):
           yield NOT_MODIFIED

   **APPEND**

   **APPEND** tells bonobo to append this output to the input (positional arguments will equal `input_args + output_args`,
   keyword arguments will equal `{**input_kwargs, **output_kwargs}`).

   *CAN be combined, but not with itself*

   .. code-block:: python

       from bonobo import APPEND

       def output_will_be_appended_to_input(*args, **kwargs):
           yield APPEND, 'foo', 'bar', {'eat_at': 'joe'}

   **LOOPBACK**

   **LOOPBACK** tells bonobo that this output must be looped back into our own input queue, allowing to create the stream
   processing version of recursive algorithms.

   *CAN be combined, but not with itself*

   .. code-block:: python

       from bonobo import LOOPBACK

       def output_will_be_sent_to_self(*args, **kwargs):
           yield LOOPBACK, 'Hello, I am the future "you".'

   **CHANNEL(...)**

   **CHANNEL(...)** tells bonobo that this output does not use the default channel and is routed through another path.
   This is something you should probably not use unless your data flow design is complex, and if you're not certain
   about it, it probably means that it is not the feature you're looking for.

   *CAN be combined, but not with itself*

   .. code-block:: python

      from bonobo import CHANNEL

      def output_will_be_sent_to_self(*args, **kwargs):
          yield CHANNEL("errors"), 'That is not cool.'

2. Once all flags are "consumed", the remaining part is interpreted.

   * If it is a :class:`bonobo.Bag` instance, then it's used directly.
   * If it is a :class:`dict` then a kwargs-only :class:`bonobo.Bag` will be created.
   * If it is a :class:`tuple` then an args-only :class:`bonobo.Bag` will be created, unless its last argument is a
     :class:`dict` in which case a args+kwargs :class:`bonobo.Bag` will be created.
   * If it's something else, it will be used to create a one-arg-only :class:`bonobo.Bag`.

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
        def __call__(self, s: str) -> str:
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

