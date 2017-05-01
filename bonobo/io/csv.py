import csv

from bonobo.config import Option
from bonobo.config.processors import ContextProcessor, contextual
from bonobo.util.objects import ValueHolder
from .file import FileHandler, FileReader, FileWriter


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
    headers = Option(tuple)


class CsvReader(CsvHandler, FileReader):
    """
    Reads a CSV and yield the values as dicts.

    .. attribute:: skip

        The amount of lines to skip before it actually yield output.

    """

    skip = Option(int, default=0)

    @ContextProcessor
    def csv_headers(self, context, fs, file):
        yield ValueHolder(self.headers)

    def read(self, fs, file, headers):
        reader = csv.reader(file, delimiter=self.delimiter, quotechar=self.quotechar)
        headers.value = headers.value or next(reader)
        field_count = len(headers.value)

        if self.skip and self.skip > 0:
            for _ in range(0, self.skip):
                next(reader)

        for row in reader:
            if len(row) != field_count:
                raise ValueError('Got a line with %d fields, expecting %d.' % (len(row), field_count, ))

            yield dict(zip(headers.value, row))


class CsvWriter(CsvHandler, FileWriter):
    @ContextProcessor
    def writer(self, context, fs, file, lineno):
        writer = csv.writer(file, delimiter=self.delimiter, quotechar=self.quotechar, lineterminator=self.eol)
        headers = ValueHolder(list(self.headers) if self.headers else None)
        yield writer, headers

    def write(self, fs, file, lineno, writer, headers, row):
        if not lineno.value:
            headers.value = headers.value or row.keys()
            writer.writerow(headers.value)
        writer.writerow(row[header] for header in headers.value)
        lineno.value += 1
