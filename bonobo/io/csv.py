import csv
from copy import copy

from .file import FileReader, FileWriter, FileHandler


class CsvHandler(FileHandler):
    delimiter = ';'
    quotechar = '"'
    headers = None


class CsvReader(CsvHandler, FileReader):
    """
    Reads a CSV and yield the values as dicts.

    .. attribute:: delimiter

        The CSV delimiter.

    .. attribute:: quotechar

        The CSV quote character.

    .. attribute:: headers

        The list of column names, if the CSV does not contain it as its first line.

    .. attribute:: skip

        The amount of lines to skip before it actually yield output.

    """

    skip = 0

    def __init__(self, path_or_buf, delimiter=None, quotechar=None, headers=None, skip=None):
        super().__init__(path_or_buf)

        self.delimiter = str(delimiter or self.delimiter)
        self.quotechar = quotechar or self.quotechar
        self.headers = headers or self.headers
        self.skip = skip or self.skip

    @property
    def has_headers(self):
        return bool(self.headers)

    def read(self, ctx):
        reader = csv.reader(ctx.file, delimiter=self.delimiter, quotechar=self.quotechar)
        headers = self.has_headers and self.headers or next(reader)
        field_count = len(headers)

        if self.skip and self.skip > 0:
            for i in range(0, self.skip):
                next(reader)

        for row in reader:
            if len(row) != field_count:
                raise ValueError('Got a line with %d fields, expecting %d.' % (
                    len(row),
                    field_count, ))

            yield dict(zip(headers, row))


class CsvWriter(CsvHandler, FileWriter):
    def __init__(self, path_or_buf, delimiter=None, quotechar=None, headers=None):
        super().__init__(path_or_buf)

        self.delimiter = str(delimiter or self.delimiter)
        self.quotechar = quotechar or self.quotechar
        self.headers = headers or self.headers

    def initialize(self, ctx):
        super().initialize(ctx)
        ctx.writer = csv.writer(ctx.file, delimiter=self.delimiter, quotechar=self.quotechar)
        ctx.headers = copy(self.headers)
        ctx.first = True

    def write(self, ctx, row):
        if ctx.first:
            ctx.headers = ctx.headers or row.keys()
            ctx.writer.writerow(ctx.headers)
            ctx.first = False
        ctx.writer.writerow(row[header] for header in ctx.headers)

    def finalize(self, ctx):
        del ctx.headers, ctx.writer, ctx.first
        super().finalize(ctx)
