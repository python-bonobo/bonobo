import functools
import html
import itertools
import pprint

from mondrian import term

from bonobo import settings
from bonobo.config import Configurable, Method, Option, use_context, use_no_input, use_raw_input
from bonobo.config.functools import transformation_factory
from bonobo.config.processors import ContextProcessor, use_context_processor
from bonobo.constants import NOT_MODIFIED
from bonobo.util.objects import ValueHolder
from bonobo.util.term import CLEAR_EOL

__all__ = [
    'FixedWindow',
    'Format',
    'Limit',
    'OrderFields',
    'PrettyPrinter',
    'Rename',
    'SetFields',
    'Tee',
    'UnpackItems',
    'count',
    'identity',
    'noop',
]


def identity(x):
    return x


class Limit(Configurable):
    """
    Creates a Limit() node, that will only let go through the first n rows (defined by the `limit` option), unmodified.

    .. attribute:: limit

        Number of rows to let go through.

    TODO: simplify into a closure building factory?

    """

    limit = Option(positional=True, default=10)

    @ContextProcessor
    def counter(self, context):
        yield ValueHolder(0)

    def __call__(self, counter, *args, **kwargs):
        counter += 1
        if counter <= self.limit:
            yield NOT_MODIFIED


def Tee(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        nonlocal f
        f(*args, **kwargs)
        return NOT_MODIFIED

    return wrapped


def _shorten(s, w):
    if w and len(s) > w:
        s = s[0 : w - 3] + '...'
    return s


class PrettyPrinter(Configurable):
    max_width = Option(
        int,
        default=term.get_size()[0],
        required=False,
        __doc__='''
        If set, truncates the output values longer than this to this width.
    ''',
    )

    filter = Method(
        default=(
            lambda self, index, key, value: (value is not None)
            and (not isinstance(key, str) or not key.startswith('_'))
        ),
        __doc__='''
            A filter that determine what to print.
            
            Default is to ignore any key starting with an underscore and none values.
        ''',
    )

    @ContextProcessor
    def context(self, context):
        context.setdefault('_jupyter_html', None)
        yield context
        if context._jupyter_html is not None:
            from IPython.display import display, HTML

            display(HTML('\n'.join(['<table>'] + context._jupyter_html + ['</table>'])))

    def __call__(self, context, *args, **kwargs):
        if not settings.QUIET:
            if term.isjupyter:
                self.print_jupyter(context, *args, **kwargs)
                return NOT_MODIFIED
            if term.istty:
                self.print_console(context, *args, **kwargs)
                return NOT_MODIFIED

        self.print_quiet(context, *args, **kwargs)
        return NOT_MODIFIED

    def print_quiet(self, context, *args, **kwargs):
        for index, (key, value) in enumerate(itertools.chain(enumerate(args), kwargs.items())):
            if self.filter(index, key, value):
                print(self.format_quiet(index, key, value, fields=context.get_input_fields()))

    def format_quiet(self, index, key, value, *, fields=None):
        # XXX should we implement argnames here ?
        return ' '.join(((' ' if index else '-'), str(key), ':', str(value).strip()))

    def print_console(self, context, *args, **kwargs):
        print('\u250c')
        for index, (key, value) in enumerate(itertools.chain(enumerate(args), kwargs.items())):
            if self.filter(index, key, value):
                print(self.format_console(index, key, value, fields=context.get_input_fields()))
        print('\u2514')

    def format_console(self, index, key, value, *, fields=None):
        fields = fields or []
        if not isinstance(key, str):
            if len(fields) > key and str(key) != str(fields[key]):
                key = '{}{}'.format(fields[key], term.lightblack('[{}]'.format(key)))
            else:
                key = str(index)

        prefix = '\u2502 {} = '.format(key)
        prefix_length = len(prefix)

        def indent(text, prefix):
            for i, line in enumerate(text.splitlines()):
                yield (prefix if i else '') + line + CLEAR_EOL + '\n'

        repr_of_value = ''.join(
            indent(pprint.pformat(value, width=self.max_width - prefix_length), '\u2502' + ' ' * (len(prefix) - 1))
        ).strip()
        return '{}{}{}'.format(prefix, repr_of_value.replace('\n', CLEAR_EOL + '\n'), CLEAR_EOL)

    def print_jupyter(self, context, *args):
        if not context._jupyter_html:
            context._jupyter_html = [
                '<thead><tr>',
                *map('<th>{}</th>'.format, map(html.escape, map(str, context.get_input_fields() or range(len(args))))),
                '</tr></thead>',
            ]

        context._jupyter_html += ['<tr>', *map('<td>{}</td>'.format, map(html.escape, map(repr, args))), '</tr>']


@use_no_input
def noop(*args, **kwargs):
    return NOT_MODIFIED


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
            last_value = buffer.get()
            last_value += [None] * (self.length - len(last_value))
            context.send(*last_value)

    @use_raw_input
    def __call__(self, buffer, bag):
        buffer.append(bag)
        if len(buffer) >= self.length:
            yield tuple(buffer.get())
            buffer.set([])


@transformation_factory
def OrderFields(fields):
    """
    Transformation factory to reorder fields in a data stream.

    :param fields:
    :return: callable
    """
    fields = list(fields)

    @use_context
    @use_raw_input
    def _OrderFields(context, row):
        nonlocal fields
        context.setdefault('remaining', None)
        if not context.output_type:
            context.remaining = list(sorted(set(context.get_input_fields()) - set(fields)))
            context.set_output_fields(fields + context.remaining)

        yield tuple(row.get(field) for field in context.get_output_fields())

    return _OrderFields


@transformation_factory
def SetFields(fields):
    """
    Transformation factory that sets the field names on first iteration, without touching the values.

    :param fields:
    :return: callable
    """

    @use_context
    @use_no_input
    def _SetFields(context):
        nonlocal fields
        if not context.output_type:
            context.set_output_fields(fields)
        return NOT_MODIFIED

    return _SetFields


@transformation_factory
def UnpackItems(*items, fields=None, defaults=None):
    """
    >>> UnpackItems(0)

    :param items:
    :param fields:
    :param defaults:
    :return: callable
    """
    defaults = defaults or {}

    @use_context
    @use_raw_input
    def _UnpackItems(context, bag):
        nonlocal fields, items, defaults

        if fields is None:
            fields = ()
            for item in items:
                fields += tuple(bag[item].keys())
            context.set_output_fields(fields)

        values = ()
        for item in items:
            values += tuple(bag[item].get(field, defaults.get(field)) for field in fields)

        return values

    return _UnpackItems


@transformation_factory
def Rename(**translations):
    # XXX todo handle duplicated

    fields = None
    translations = {v: k for k, v in translations.items()}

    @use_context
    @use_raw_input
    def _Rename(context, bag):
        nonlocal fields, translations

        if not fields:
            fields = tuple(translations.get(field, field) for field in context.get_input_fields())
            context.set_output_fields(fields)

        return NOT_MODIFIED

    return _Rename


@transformation_factory
def Format(**formats):
    fields, newfields = None, None

    @use_context
    @use_raw_input
    def _Format(context, bag):
        nonlocal fields, newfields, formats

        if not context.output_type:
            fields = context.input_type._fields
            newfields = tuple(field for field in formats if not field in fields)
            context.set_output_fields(fields + newfields)

        return tuple(
            formats[field].format(**bag._asdict()) if field in formats else bag.get(field)
            for field in fields + newfields
        )

    return _Format


def _count(self, context):
    counter = yield ValueHolder(0)
    context.send(counter.get())


@use_no_input
@use_context_processor(_count)
def count(counter):
    counter += 1
