""" Various simple utilities. """

import functools
import pprint

from .tokens import NotModified

__all__ = [
    'NotModified',
    'head',
    'log',
    'noop',
    'tee',
]


def head(n=10):
    i = 0

    def _head(x):
        nonlocal i, n
        i += 1
        if i <= n:
            yield x

    _head.__name__ = 'head({})'.format(n)
    return _head


def tee(f):
    @functools.wraps(f)
    def wrapped(x):
        nonlocal f
        f(x)
        return x

    return wrapped


log = tee(pprint.pprint)


def noop(*args, **kwargs):
    pass
