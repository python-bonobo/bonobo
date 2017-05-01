import functools
from pprint import pprint as _pprint

from colorama import Fore, Style

from bonobo.config.processors import ContextProcessor
from bonobo.structs.bags import Bag
from bonobo.util.objects import ValueHolder
from bonobo.util.term import CLEAR_EOL

__all__ = [
    'identity',
    'Limit',
    'Tee',
    'count',
    'pprint',
    'PrettyPrint',
    'noop',
]


def identity(x):
    return x


def Limit(n=10):
    from bonobo.constants import NOT_MODIFIED
    i = 0

    def _limit(*args, **kwargs):
        nonlocal i, n
        i += 1
        if i <= n:
            yield NOT_MODIFIED

    _limit.__name__ = 'Limit({})'.format(n)
    return _limit


def Tee(f):
    from bonobo.constants import NOT_MODIFIED

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        nonlocal f
        f(*args, **kwargs)
        return NOT_MODIFIED

    return wrapped


def count(counter, *args, **kwargs):
    counter += 1


@ContextProcessor.decorate(count)
def _count_counter(self, context):
    counter = ValueHolder(0)
    yield counter
    context.send(Bag(counter.value))


pprint = Tee(_pprint)


def PrettyPrint(title_keys=('title', 'name', 'id'), print_values=True, sort=True):
    from bonobo.constants import NOT_MODIFIED

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
    from bonobo.constants import NOT_MODIFIED
    return NOT_MODIFIED
