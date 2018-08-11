import csv

from bonobo.config import Option, use_context
from bonobo.config.options import Method, RenamedOption
from bonobo.constants import NOT_MODIFIED
from bonobo.nodes.io.base import FileHandler
from bonobo.nodes.io.file import FileReader, FileWriter
from bonobo.util import ensure_tuple


class CsvHandler(FileHandler):
    """

    .. attribute:: delimiter

        The CSV delimiter.

    .. attribute:: quotechar

        The CSV quote character.

    .. attribute:: fields

        The list of column names, if the CSV does not contain it as its first line.

    """

    # Dialect related options
    delimiter = Option(str, default=csv.excel.delimiter, required=False)
    quotechar = Option(str, default=csv.excel.quotechar, required=False)
    escapechar = Option(str, default=csv.excel.escapechar, required=False)
    doublequote = Option(str, default=csv.excel.doublequote, required=False)
    skipinitialspace = Option(str, default=csv.excel.skipinitialspace, required=False)
    lineterminator = Option(str, default=csv.excel.lineterminator, required=False)
    quoting = Option(int, default=csv.excel.quoting, required=False)

    # Fields (renamed from headers)
    headers = RenamedOption('fields')
    fields = Option(ensure_tuple, required=False)

    def get_dialect_kwargs(self):
        return {
            'delimiter': self.delimiter,
            'quotechar': self.quotechar,
            'escapechar': self.escapechar,
            'doublequote': self.doublequote,
            'skipinitialspace': self.skipinitialspace,
            'lineterminator': self.lineterminator,
            'quoting': self.quoting,
        }


@use_context
class CsvReader(FileReader, CsvHandler):
    """
    Reads a CSV and yield the values as dicts.
    """

    skip = Option(
        int,
        default=0,
        __doc__='''
        If set and greater than zero, the reader will skip this amount of lines.
    ''',
    )

    @Method(
        positional=False,
        __doc__='''
            Builds the CSV reader, a.k.a an object we can iterate, each iteration giving one line of fields, as an
            iterable.
            
            Defaults to builtin csv.reader(...), but can be overriden to fit your special needs.
        ''',
    )
    def reader_factory(self, file):
        return csv.reader(file, **self.get_dialect_kwargs())

    def read(self, file, context, *, fs):
        context.setdefault('skipped', 0)
        reader = self.reader_factory(file)
        skip = self.skip

        if not context.output_type:
            context.set_output_fields(self.fields or next(reader))

        for row in reader:
            if context.skipped < skip:
                context.skipped += 1
                continue
            yield tuple(row)

    __call__ = read


@use_context
class CsvWriter(FileWriter, CsvHandler):
    @Method(
        __doc__='''
            Builds the CSV writer, a.k.a an object we can pass a field collection to be written as one line in the
            target file.
            
            Defaults to builtin csv.writer(...).writerow, but can be overriden to fit your special needs.
        '''
    )
    def writer_factory(self, file):
        return csv.writer(file, **self.get_dialect_kwargs()).writerow

    def write(self, file, context, *values, fs):
        context.setdefault('lineno', 0)
        fields = context.get_input_fields()

        if not context.lineno:
            context.writer = self.writer_factory(file)

            if fields:
                context.writer(fields)
                context.lineno += 1

        if fields:
            if len(values) != len(fields):
                raise ValueError(
                    'Values length differs from input fields length. Expected: {}. Got: {}. Values: {!r}.'.format(
                        len(fields), len(values), values
                    )
                )
            context.writer(values)
        else:
            for arg in values:
                context.writer(ensure_tuple(arg))

        return NOT_MODIFIED

    __call__ = write
