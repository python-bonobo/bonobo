import csv
import warnings

from bonobo.config import Option, ContextProcessor
from bonobo.config.options import RemovedOption, Method
from bonobo.constants import NOT_MODIFIED, ARGNAMES
from bonobo.nodes.io.base import FileHandler
from bonobo.nodes.io.file import FileReader, FileWriter
from bonobo.structs.bags import Bag
from bonobo.util import ensure_tuple


class CsvHandler(FileHandler):
    """

    .. attribute:: delimiter

        The CSV delimiter.

    .. attribute:: quotechar

        The CSV quote character.

    .. attribute:: headers

        The list of column names, if the CSV does not contain it as its first line.

    """
    delimiter = Option(str, default=';')
    quotechar = Option(str, default='"')
    headers = Option(ensure_tuple, required=False)
    ioformat = RemovedOption(positional=False, value='kwargs')


class CsvReader(FileReader, CsvHandler):
    """
    Reads a CSV and yield the values as dicts.

    .. attribute:: skip

        The amount of lines to skip before it actually yield output.

    """

    skip = Option(int, default=0)

    @Method(
        __doc__='''
            Builds the CSV reader, a.k.a an object we can iterate, each iteration giving one line of fields, as an
            iterable.
            
            Defaults to builtin csv.reader(...), but can be overriden to fit your special needs.
        '''
    )
    def reader_factory(self, file):
        return csv.reader(file, delimiter=self.delimiter, quotechar=self.quotechar)

    def read(self, fs, file):
        reader = self.reader_factory(file)
        headers = self.headers or next(reader)
        for row in reader:
            yield Bag(*row, **{ARGNAMES: headers})


class CsvWriter(FileWriter, CsvHandler):
    @ContextProcessor
    def context(self, context, *args):
        yield context

    @Method(
        __doc__='''
            Builds the CSV writer, a.k.a an object we can pass a field collection to be written as one line in the
            target file.
            
            Defaults to builtin csv.writer(...).writerow, but can be overriden to fit your special needs.
        '''
    )
    def writer_factory(self, file):
        return csv.writer(file, delimiter=self.delimiter, quotechar=self.quotechar, lineterminator=self.eol).writerow

    def write(self, fs, file, lineno, context, *args, _argnames=None):
        try:
            writer = context.writer
        except AttributeError:
            context.writer = self.writer_factory(file)
            writer = context.writer
            context.headers = self.headers or _argnames

        if context.headers and not lineno:
            writer(context.headers)

        lineno += 1

        if context.headers:
            try:
                row = [args[i] for i, header in enumerate(context.headers) if header]
            except IndexError:
                warnings.warn(
                    'At line #{}, expected {} fields but only got {}. Padding with empty strings.'.format(
                        lineno, len(context.headers), len(args)
                    )
                )
                row = [(args[i] if i < len(args) else '') for i, header in enumerate(context.headers) if header]
        else:
            row = args

        writer(row)

        return NOT_MODIFIED
