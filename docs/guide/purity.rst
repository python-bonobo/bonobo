Pure transformations
====================

The nature of components, and how the data flow from one to another, make them not so easy to write correctly.
Hopefully, with a few hints, you will be able to understand why and how they should be written.

The major problem we have is that one message can go through more than one component, and at the same time. If you
wanna be safe, you tend to :func:`copy.copy()` everything between two calls to two different components, but that
will mean that a lot of useless memory space would be taken for copies that are never modified.

Instead of that, we chosed the oposite: copies are never made, and you should not modify in place the inputs of your
component before yielding them, and that mostly means that you want to recreate dicts and lists before yielding (or
returning) them. Numeric values, strings and tuples being immutable in python, modifying a variable of one of those
type will already return a different instance.

Numbers
:::::::

You can't be wrong with numbers. All of the following are correct.

.. code-block:: python

    def do_your_number_thing(n: int) -> int:
        return n

    def do_your_number_thing(n: int) -> int:
        yield n

    def do_your_number_thing(n: int) -> int:
        return n + 1

    def do_your_number_thing(n: int) -> int:
        yield n + 1

    def do_your_number_thing(n: int) -> int:
        # correct, but bad style
        n += 1
        return n

    def do_your_number_thing(n: int) -> int:
        # correct, but bad style
        n += 1
        yield n

The same is true with other numeric types, so don't be shy. Operate like crazy, my friend.

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

You know the drill, strings are immutable, blablabla ... Examples left as an exercise for the reader.

Dicts
:::::

So, now it gets interesting. Dicts are mutable. It means that you can mess things up badly here if you're not cautious.

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
transformation graph, and mutations will be seen in components downwards the output, but also upward. Let's see
a more obvious example of something you should not do:

.. code-block:: python

    def mutate_my_dict_and_yield() -> dict:
        d = {}
        for i in range(100):
            # Bad! Don't do that!
            d['index'] = i
            yield d

Here, the same dict is yielded in each iteration, and its state when the next component in chain is called is undetermined.

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

I hear you think «Yeah, but if I create like millions of dicts ...». The answer is simple. Using dicts like this will
create a lot, but also free a lot because as soon as all the future components that take this dict as input are done,
the dict will be garbage collected. Youplaboum!



