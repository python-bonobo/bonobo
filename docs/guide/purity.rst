Pure transformations
====================

The nature of components, and how the data flow from one to another, can be a bit tricky.
Hopefully, they should be very easy to write with a few hints.

The major problem we have is that one message (underlying implementation: :class:`bonobo.structs.bags.Bag`) can go
through more than one component, and at the same time. If you wanna be safe, you tend to :func:`copy.copy()` everything
between two calls to two different components, but that's very expensive.

Instead of that, we chosed the oposite: copies are never made, and you should not modify in place the inputs of your
component before yielding them, and that mostly means that you want to recreate dicts and lists before yielding (or
returning) them. Numeric values, strings and tuples being immutable in python, modifying a variable of one of those
type will already return a different instance.

Examples will be shown with `return` statements, of course you can do the same with `yield` statements in generators.

Numbers
:::::::

In python, numbers are immutable. So you can't be wrong with numbers. All of the following are correct.

.. code-block:: python

    def do_your_number_thing(n: int) -> int:
        return n

    def do_your_number_thing(n: int) -> int:
        return n + 1

    def do_your_number_thing(n: int) -> int:
        # correct, but bad style
        n += 1
        return n

The same is true with other numeric types, so don't be shy.


Tuples
::::::

Tuples are immutable, so you risk nothing.

.. code-block:: python

    def do_your_tuple_thing(t: tuple) -> tuple:
        return ('foo', ) + t

    def do_your_tuple_thing(t: tuple) -> tuple:
        return t + ('bar', )

    def do_your_tuple_thing(t: tuple) -> tuple:
        # correct, but bad style
        t += ('baaaz', )
        return t

Strings
:::::::

You know the drill, strings are immutable.

.. code-block:: python

    def do_your_str_thing(t: str) -> str:
        return 'foo ' + t + ' bar'

    def do_your_str_thing(t: str) -> str:
        return ' '.join(('foo', t, 'bar', ))

    def do_your_str_thing(t: str) -> str:
        return 'foo {} bar'.format(t)

You can, if you're using python 3.6+, use `f-strings <https://docs.python.org/3/reference/lexical_analysis.html#f-strings>`_,
but the core bonobo libraries won't use it to stay 3.5 compatible.


Dicts
:::::

So, now it gets interesting. Dicts are mutable. It means that you can mess things up if you're not cautious.

For example, doing the following may cause unexpected problems:

.. code-block:: python

    def mutate_my_dict_like_crazy(d: dict) -> dict:
        # Bad! Don't do that!
        d.update({
            'foo': compute_something()
        })
        # Still bad! Don't mutate the dict!
        d['bar'] = compute_anotherthing()
        return d

The problem is easy to understand: as **Bonobo** won't make copies of your dict, the same dict will be passed along the
transformation graph, and mutations will be seen in components downwards the output (and also upward). Let's see
a more obvious example of something you should *not* do:

.. code-block:: python

    def mutate_my_dict_and_yield() -> dict:
        d = {}
        for i in range(100):
            # Bad! Don't do that!
            d['index'] = i
            yield d

Here, the same dict is yielded in each iteration, and its state when the next component in chain is called is undetermined
(how many mutations happened since the `yield`? Hard to tell...).

Now let's see how to do it correctly:

.. code-block:: python

    def new_dicts_like_crazy(d: dict) -> dict:
        # Creating a new dict is correct.
        return {
            **d,
            'foo': compute_something(),
            'bar': compute_anotherthing(),
        }

    def new_dict_and_yield() -> dict:
        d = {}
        for i in range(100):
            # Different dict each time.
            yield {
                'index': i
            }

I hear you think «Yeah, but if I create like millions of dicts ...».

Let's say we chosed the oposite way and copy the dict outside the transformation (in fact, `it's what we did in bonobo's
ancestor <https://github.com/rdcli/rdc.etl/blob/dev/rdc/etl/io/__init__.py#L187>`_). This means you will also create the
same number of dicts, the difference is that you won't even notice it. Also, it means that if you want to yield 1 million
times the same dict, going "pure" makes it efficient (you'll just yield the same object 1 million times) while going "copy
crazy" will create 1 million objects.

Using dicts like this will create a lot of dicts, but also free them as soon as all the future components that take this dict
as input are done. Also, one important thing to note is that most primitive data structures in python are immutable, so creating
a new dict will of course create a new envelope, but the unchanged objects inside won't be duplicated.

Last thing, copies made in the "pure" approach are explicit, and usually, explicit is better than implicit.

