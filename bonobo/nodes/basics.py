import functools
import itertools

from bonobo import settings
from bonobo.config import Configurable, Option
from bonobo.config.processors import ContextProcessor
from bonobo.constants import NOT_MODIFIED, ARGNAMES
from bonobo.structs.bags import Bag
from bonobo.util.objects import ValueHolder
from bonobo.util.term import CLEAR_EOL

__all__ = [
    'FixedWindow',
    'Limit',
    'PrettyPrinter',
    'Tee',
    'Update',
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


def _shorten(s, w):
    if w and len(s) > w:
        s = s[0:w - 3] + '...'
    return s


class PrettyPrinter(Configurable):
    max_width = Option(
        int,
        required=False,
        __doc__='''
        If set, truncates the output values longer than this to this width.
    '''
    )

    def call(self, *args, **kwargs):
        formater = self._format_quiet if settings.QUIET.get() else self._format_console
        argnames = kwargs.get(ARGNAMES, None)

        for i, (item, value) in enumerate(
            itertools.chain(enumerate(args), filter(lambda x: not x[0].startswith('_'), kwargs.items()))
        ):
            print(formater(i, item, value, argnames=argnames))

    def _format_quiet(self, i, item, value, *, argnames=None):
        # XXX should we implement argnames here ?
        return ' '.join(((' ' if i else '-'), str(item), ':', str(value).strip()))

    def _format_console(self, i, item, value, *, argnames=None):
        argnames = argnames or []
        if not isinstance(item, str):
            if len(argnames) >= item:
                item = '{} / {}'.format(item, argnames[item])
            else:
                item = str(i)

        return ' '.join(
            (
                (' ' if i else '•'), item, '=', _shorten(str(value).strip(),
                                                         self.max_width).replace('\n', '\n' + CLEAR_EOL), CLEAR_EOL
            )
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


def Update(*consts, **kwconsts):
    """
    Transformation factory to update a stream with constant values, by appending to args and updating kwargs.

    :param consts: what to append to the input stream args
    :param kwconsts: what to use to update input stream kwargs
    :return: function

    """

    def update(*args, **kwargs):
        nonlocal consts, kwconsts
        return (*args, *consts, {**kwargs, **kwconsts})

    update.__name__ = 'Update({})'.format(Bag.format_args(*consts, **kwconsts))

    return update


class FixedWindow(Configurable):
    """
    Transformation factory to create fixed windows of inputs, as lists.

    For example, if the input is successively 1, 2, 3, 4, etc. and you pass it through a ``FixedWindow(2)``, you'll get
    lists of elements 2 by 2: [1, 2], [3, 4], ...

    """

    length = Option(int, positional=True)  # type: int

    @ContextProcessor
    def buffer(self, context):
        buffer = yield ValueHolder([])
        if len(buffer):
            context.send(Bag(buffer.get()))

    def call(self, buffer, x):
        buffer.append(x)
        if len(buffer) >= self.length:
            yield buffer.get()
            buffer.set([])
