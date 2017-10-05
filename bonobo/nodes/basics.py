import functools
import itertools

from bonobo import settings
from bonobo.config import Configurable, Option
from bonobo.config.processors import ContextProcessor
from bonobo.structs.bags import Bag
from bonobo.util.objects import ValueHolder
from bonobo.util.term import CLEAR_EOL

from bonobo.constants import NOT_MODIFIED

__all__ = [
    'Limit',
    'PrettyPrinter',
    'Tee',
    'arg0_to_kwargs',
    'count',
    'identity',
    'kwargs_to_arg0',
    'noop',
]


def identity(x):
    return x


class Limit(Configurable):
    """
    Creates a Limit() node, that will only let go through the first n rows (defined by the `limit` option), unmodified.

    .. attribute:: limit

        Number of rows to let go through.

    """
    limit = Option(positional=True, default=10)

    @ContextProcessor
    def counter(self, context):
        yield ValueHolder(0)

    def call(self, counter, *args, **kwargs):
        counter += 1
        if counter <= self.limit:
            yield NOT_MODIFIED


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
    context.send(Bag(counter._value))


class PrettyPrinter(Configurable):
    def call(self, *args, **kwargs):
        formater = self._format_quiet if settings.QUIET.get() else self._format_console

        for i, (item, value) in enumerate(itertools.chain(enumerate(args), kwargs.items())):
            print(formater(i, item, value))

    def _format_quiet(self, i, item, value):
        return ' '.join(((' ' if i else '-'), str(item), ':', str(value).strip()))

    def _format_console(self, i, item, value):
        return ' '.join(
            ((' ' if i else '•'), str(item), '=', str(value).strip().replace('\n', '\n' + CLEAR_EOL), CLEAR_EOL)
        )


def noop(*args, **kwargs):  # pylint: disable=unused-argument
    from bonobo.constants import NOT_MODIFIED
    return NOT_MODIFIED


def arg0_to_kwargs(row):
    """
    Transform items in a stream from "arg0" format (each call only has one positional argument, which is a dict-like
    object) to "kwargs" format (each call only has keyword arguments that represent a row).

    :param row:
    :return: bonobo.Bag
    """
    return Bag(**row)


def kwargs_to_arg0(**row):
    """
    Transform items in a stream from "kwargs" format (each call only has keyword arguments that represent a row) to
    "arg0" format (each call only has one positional argument, which is a dict-like object) .

    :param **row:
    :return: bonobo.Bag
    """
    return Bag(row)
