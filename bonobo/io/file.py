from io import BytesIO

from bonobo.config import Configurable, Option
from bonobo.context import ContextProcessor
from bonobo.context.processors import contextual
from bonobo.util.objects import ValueHolder

__all__ = [
    'FileReader',
    'FileWriter',
]


@contextual
class FileHandler(Configurable):
    """
    Abstract component factory for file-related components.

    """

    path = Option(str, required=True)
    eol = Option(str, default='\n')
    mode = Option(str)

    @ContextProcessor
    def file(self, context):
        if self.path.find('http://') == 0 or self.path.find('https://') == 0:
            import requests
            response = requests.get(self.path)
            yield BytesIO(response.content)
        else:
            with self.open() as file:
                yield file

    def open(self):
        return open(self.path, self.mode)


class Reader(FileHandler):
    def __call__(self, *args):
        yield from self.read(*args)

    def read(self, *args):
        raise NotImplementedError('Abstract.')


class Writer(FileHandler):
    def __call__(self, *args):
        return self.write(*args)

    def write(self, *args):
        raise NotImplementedError('Abstract.')


class FileReader(Reader):
    """
    Component factory for file-like readers.

    On its own, it can be used to read a file and yield one row per line, trimming the "eol" character at the end if
    present. Extending it is usually the right way to create more specific file readers (like json, csv, etc.)

    """

    mode = Option(str, default='r')

    def read(self, file):
        """
        Write a row on the next line of given file.
        Prefix is used for newlines.

        :param ctx:
        :param row:
        """
        for line in file:
            yield line.rstrip(self.eol)


@contextual
class FileWriter(Writer):
    """
    Component factory for file or file-like writers.

    On its own, it can be used to write in a file one line per row that comes into this component. Extending it is
    usually the right way to create more specific file writers (like json, csv, etc.)

    """

    mode = Option(str, default='w+')

    @ContextProcessor
    def lineno(self, context, file):
        lineno = ValueHolder(0, type=int)
        yield lineno

    def write(self, file, lineno, row):
        """
        Write a row on the next line of opened file in context.

        :param file fp:
        :param str row:
        :param str prefix:
        """
        self._write_line(file, (self.eol if lineno.value else '') + row)
        lineno.value += 1

    def _write_line(self, file, line):
        return file.write(line)
