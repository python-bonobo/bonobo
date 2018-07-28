import bisect
import functools


class sortedlist(list):
    def insort(self, x):
        bisect.insort(self, x)


def _with_length_check(f):
    @functools.wraps(f)
    def _wrapped(*args, length=None, **kwargs):
        nonlocal f
        result = f(*args, **kwargs)
        if length is not None:
            if length != len(result):
                raise TypeError(
                    'Length check failed, expected {} fields but got {}: {!r}.'.format(length, len(result), result)
                )
        return result

    return _wrapped


@_with_length_check
def ensure_tuple(tuple_or_mixed, *, cls=None):
    """
    If it's not a tuple, let's make a tuple of one item.
    Otherwise, not changed.

    :param tuple_or_mixed:
    :return: tuple

    """
    if cls is None:
        cls = tuple

    if isinstance(tuple_or_mixed, cls):
        return tuple_or_mixed

    if tuple_or_mixed is None:
        return tuple.__new__(cls, ())

    if isinstance(tuple_or_mixed, tuple):
        return tuple.__new__(cls, tuple_or_mixed)

    return tuple.__new__(cls, (tuple_or_mixed, ))


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
