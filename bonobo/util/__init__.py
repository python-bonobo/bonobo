""" Various simple utilities. """

import functools
import pprint

from .tokens import NOT_MODIFIED
from .helpers import run, console_run, jupyter_run

__all__ = [
    'NOT_MODIFIED',
    'console_run',
    'head',
    'jupyter_run',
    'log',
    'noop',
    'run',
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


def noop(*args, **kwargs):  # pylint: disable=unused-argument
    pass
