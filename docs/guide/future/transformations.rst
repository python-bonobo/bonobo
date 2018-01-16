Transformations
===============

.. warning::

   This is a "future" document, that does not exist, it's only kept here not to lose the data until we organize better
   documentation versioning.


Output
------

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

2. Once all flags are "consumed", the remaining part is interpreted.

   * If it is a :class:`bonobo.Bag` instance, then it's used directly.
   * If it is a :class:`dict` then a kwargs-only :class:`bonobo.Bag` will be created.
   * If it is a :class:`tuple` then an args-only :class:`bonobo.Bag` will be created, unless its last argument is a
     :class:`dict` in which case a args+kwargs :class:`bonobo.Bag` will be created.
   * If it's something else, it will be used to create a one-arg-only :class:`bonobo.Bag`.

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

