import csv

from bonobo.config import Option
from bonobo.config.processors import ContextProcessor
from bonobo.constants import NOT_MODIFIED
from bonobo.errors import ConfigurationError, ValidationError
from bonobo.structs import Bag
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


def validate_csv_output_format(v):
    if callable(v):
        return v
    if v in {'dict', 'kwargs'}:
        return v
    raise ValidationError('Unsupported format {!r}.'.format(v))


class CsvReader(CsvHandler, FileReader):
    """
    Reads a CSV and yield the values as dicts.

    .. attribute:: skip

        The amount of lines to skip before it actually yield output.

    """

    skip = Option(int, default=0)
    output_format = Option(validate_csv_output_format, default='dict')

    @ContextProcessor
    def csv_headers(self, context, fs, file):
        yield ValueHolder(self.headers)

    def get_output_formater(self):
        if callable(self.output_format):
            return self.output_format
        elif isinstance(self.output_format, str):
            return getattr(self, '_format_as_' + self.output_format)
        else:
            raise ConfigurationError('Unsupported format {!r} for {}.'.format(self.output_format, type(self).__name__))

    def read(self, fs, file, headers):
        reader = csv.reader(file, delimiter=self.delimiter, quotechar=self.quotechar)
        formater = self.get_output_formater()

        if not headers.get():
            headers.set(next(reader))

        field_count = len(headers)

        if self.skip and self.skip > 0:
            for _ in range(0, self.skip):
                next(reader)

        for row in reader:
            if len(row) != field_count:
                raise ValueError('Got a line with %d fields, expecting %d.' % (len(row), field_count, ))

            yield formater(headers.get(), row)

    def _format_as_dict(self, headers, values):
        return dict(zip(headers, values))

    def _format_as_kwargs(self, headers, values):
        return Bag(**dict(zip(headers, values)))


class CsvWriter(CsvHandler, FileWriter):
    @ContextProcessor
    def writer(self, context, fs, file, lineno):
        writer = csv.writer(file, delimiter=self.delimiter, quotechar=self.quotechar, lineterminator=self.eol)
        headers = ValueHolder(list(self.headers) if self.headers else None)
        yield writer, headers

    def write(self, fs, file, lineno, writer, headers, row):
        if not lineno:
            headers.set(headers.value or row.keys())
            writer.writerow(headers.get())
        writer.writerow(row[header] for header in headers.get())
        lineno += 1
        return NOT_MODIFIED
