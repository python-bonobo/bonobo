from bonobo.config import Option, Service
from bonobo.config.configurables import Configurable
from bonobo.config.processors import ContextProcessor, contextual
from bonobo.util.objects import ValueHolder

__all__ = [
    'FileReader',
    'FileWriter',
]


class FileHandler(Configurable):
    """Abstract component factory for file-related components.
    
    Args:
        path (str): which path to use within the provided filesystem.
        eol (str): which character to use to separate lines.
        mode (str): which mode to use when opening the file.
        fs (str): service name to use for filesystem.
    """

    path = Option(str, required=True, positional=True)  # type: str
    eol = Option(str, default='\n')  # type: str
    mode = Option(str)  # type: str

    fs = Service('fs')  # type: str

    @ContextProcessor
    def file(self, context, fs):
        with self.open(fs) as file:
            yield file

    def open(self, fs):
        return fs.open(self.path, self.mode)


class Reader(FileHandler):
    """Abstract component factory for readers.
    """

    def __call__(self, *args):
        yield from self.read(*args)

    def read(self, *args):
        raise NotImplementedError('Abstract.')


class Writer(FileHandler):
    """Abstract component factory for writers.
    """

    def __call__(self, *args):
        return self.write(*args)

    def write(self, *args):
        raise NotImplementedError('Abstract.')


class FileReader(Reader):
    """Component factory for file-like readers.

    On its own, it can be used to read a file and yield one row per line, trimming the "eol" character at the end if
    present. Extending it is usually the right way to create more specific file readers (like json, csv, etc.)
    """

    mode = Option(str, default='r')

    def read(self, fs, file):
        """
        Write a row on the next line of given file.
        Prefix is used for newlines.
        """
        for line in file:
            yield line.rstrip(self.eol)


class FileWriter(Writer):
    """Component factory for file or file-like writers.

    On its own, it can be used to write in a file one line per row that comes into this component. Extending it is
    usually the right way to create more specific file writers (like json, csv, etc.)
    """

    mode = Option(str, default='w+')

    @ContextProcessor
    def lineno(self, context, fs, file):
        lineno = ValueHolder(0, type=int)
        yield lineno

    def write(self, fs, file, lineno, row):
        """
        Write a row on the next line of opened file in context.
        """
        self._write_line(file, (self.eol if lineno.value else '') + row)
        lineno.value += 1

    def _write_line(self, file, line):
        return file.write(line)
