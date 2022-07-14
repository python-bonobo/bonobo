import bisect
import functools
from collections.abc import Sequence


class sortedlist(list):
    """
    A list with an insort() method that wan be used to maintain sorted lists. The list by itself is not sorted, it's
    up to the user to not insert unsorted elements.
    """

    def insort(self, x):
        """
        If the list is sorted, insert the element in the right place. Otherwise, unpredictable behaviour.

        :param x:
        """
        bisect.insort(self, x)


def _with_length_check(f):
    @functools.wraps(f)
    def _wrapped(*args, length=None, **kwargs):
        nonlocal f
        result = f(*args, **kwargs)
        if length is not None:
            if length != len(result):
                raise TypeError(
                    "Length check failed, expected {} fields but got {}: {!r}.".format(length, len(result), result)
                )
        return result

    return _wrapped


def tuple_or_const(tuple_or_mixed, *, consts=(None, False), **kwargs):
    """
    Like ensure_tuple, but also accept as valid outputs a list of constants.
    """

    if tuple_or_mixed in consts:
        return tuple_or_mixed
    if isinstance(tuple_or_mixed, str):
        pass
    elif isinstance(tuple_or_mixed, Sequence):
        tuple_or_mixed = tuple(tuple_or_mixed)
    return ensure_tuple(tuple_or_mixed, **kwargs)


@_with_length_check
def ensure_tuple(tuple_or_mixed, *, cls=None):
    """
    If it's not a tuple, let's make a tuple of one item.
    Otherwise, not changed.

    :param tuple_or_mixed: material to work on.
    :param cls: type of the resulting tuple, or `tuple` if not provided.
    :param length: provided by `_with_length_check` decorator, if specified, make sure that the tuple is of this
                   length (and raise a `TypeError` if not), otherwise, do nothing.
    :return: tuple (or something of type `cls`, if provided)
    """

    if cls is None:
        cls = tuple

    if isinstance(tuple_or_mixed, cls):
        return tuple_or_mixed

    if tuple_or_mixed is None:
        return tuple.__new__(cls, ())

    if isinstance(tuple_or_mixed, tuple):
        return tuple.__new__(cls, tuple_or_mixed)

    return tuple.__new__(cls, (tuple_or_mixed,))


def cast(type_):
    def _wrap_cast(f):
        @functools.wraps(f)
        def _wrapped_cast(*args, **kwargs):
            nonlocal f, type_
            return type_(f(*args, **kwargs))

        return _wrapped_cast

    return _wrap_cast


tuplize = cast(tuple)
tuplize.__doc__ = """
Decorates a generator and make it a tuple-returning function. As a side effect, it can also decorate any
iterator-returning function to force return value to be a tuple.

>>> tuplized_lambda = tuplize(lambda: [1, 2, 3])
>>> tuplized_lambda()
(1, 2, 3)

>>> @tuplize
... def my_generator():
...     yield 1
...     yield 2
...     yield 3
...
>>> my_generator()
(1, 2, 3)
"""


def coalesce(*values):
    """
    Returns the first argument which is not None, or None if all arguments are None.

    """

    if not len(values):
        raise ValueError("Cannot coalesce an empty list of arguments.")
    for value in values:
        if value is not None:
            return value
    return None
