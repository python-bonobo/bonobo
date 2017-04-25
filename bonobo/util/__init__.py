""" Various simple utilities. """

import functools
from pprint import pprint as _pprint

from colorama import Fore, Style

from bonobo.constants import NOT_MODIFIED
from bonobo.context.processors import contextual
from bonobo.structs.bags import Bag
from bonobo.util.objects import ValueHolder
from bonobo.util.term import CLEAR_EOL

__all__ = [
    'Limit',
    'NOT_MODIFIED',
    'PrettyPrint',
    'Tee',
    'count',
    'noop',
    'pprint',
]


def identity(x):
    return x


def Limit(n=10):
    i = 0

    def _limit(*args, **kwargs):
        nonlocal i, n
        i += 1
        if i <= n:
            yield NOT_MODIFIED

    _limit.__name__ = 'Limit({})'.format(n)
    return _limit


def Tee(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        nonlocal f
        f(*args, **kwargs)
        return NOT_MODIFIED

    return wrapped


@contextual
def count(counter, *args, **kwargs):
    counter += 1


@count.add_context_processor
def _count_counter(self, context):
    counter = ValueHolder(0)
    yield counter
    context.send(Bag(counter.value))


pprint = Tee(_pprint)


def PrettyPrint(title_keys=('title', 'name', 'id'), print_values=True, sort=True):
    def _pprint(*args, **kwargs):
        nonlocal title_keys, sort, print_values

        row = args[0]
        for key in title_keys:
            if key in row:
                print(Style.BRIGHT, row.get(key), Style.RESET_ALL, sep='')
                break

        if print_values:
            for k in sorted(row) if sort else row:
                print(
                    '  • ',
                    Fore.BLUE,
                    k,
                    Style.RESET_ALL,
                    ' : ',
                    Fore.BLACK,
                    '(',
                    type(row[k]).__name__,
                    ')',
                    Style.RESET_ALL,
                    ' ',
                    repr(row[k]),
                    CLEAR_EOL,
                )

        yield NOT_MODIFIED

    _pprint.__name__ = 'pprint'

    return _pprint


def noop(*args, **kwargs):  # pylint: disable=unused-argument
    return NOT_MODIFIED
