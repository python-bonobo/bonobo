import csv

from bonobo.config import Option
from bonobo.config.processors import ContextProcessor
from bonobo.constants import NOT_MODIFIED
from bonobo.nodes.io.base import FileHandler, IOFormatEnabled
from bonobo.nodes.io.file import FileReader, FileWriter
from bonobo.util.objects import ValueHolder


class CsvHandler(FileHandler):
    delimiter = Option(str, default=';', __doc__='''
        Delimiter used between values.
    ''')
    quotechar = Option(str, default='"', __doc__='''
        Character used for quoting values.
    ''')
    headers = Option(tuple, required=False, __doc__='''
        Tuple of headers to use, if provided.
        Readers will try to guess that from first line, unless this option is provided.
        Writers will guess from kwargs keys, unless this option is provided.
    ''')


class CsvReader(IOFormatEnabled, FileReader, CsvHandler):
    """
    Reads a CSV and yield the values as dicts.
    """

    skip = Option(int, default=0, __doc__='''
        If set and greater than zero, the reader will skip this amount of lines.
    ''')

    @ContextProcessor
    def csv_headers(self, context, fs, file):
        yield ValueHolder(self.headers)

    def read(self, fs, file, headers):
        reader = csv.reader(file, delimiter=self.delimiter, quotechar=self.quotechar)

        if not headers.get():
            headers.set(next(reader))
        _headers = headers.get()

        field_count = len(headers)

        if self.skip and self.skip > 0:
            for _ in range(0, self.skip):
                next(reader)

        for row in reader:
            if len(row) != field_count:
                raise ValueError('Got a line with %d fields, expecting %d.' % (
                    len(row),
                    field_count,
                ))

            yield self.get_output(dict(zip(_headers, row)))


class CsvWriter(IOFormatEnabled, FileWriter, CsvHandler):
    @ContextProcessor
    def writer(self, context, fs, file, lineno):
        writer = csv.writer(file, delimiter=self.delimiter, quotechar=self.quotechar, lineterminator=self.eol)
        headers = ValueHolder(list(self.headers) if self.headers else None)
        yield writer, headers

    def write(self, fs, file, lineno, writer, headers, *args, **kwargs):
        row = self.get_input(*args, **kwargs)
        if not lineno:
            headers.set(headers.value or row.keys())
            writer.writerow(headers.get())
        writer.writerow(row[header] for header in headers.get())
        lineno += 1
        return NOT_MODIFIED
