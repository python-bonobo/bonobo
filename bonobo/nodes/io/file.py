from bonobo.config import Option
from bonobo.config.processors import ContextProcessor
from bonobo.constants import NOT_MODIFIED
from bonobo.nodes.io.base import FileHandler, Reader, Writer
from bonobo.util.objects import ValueHolder


class FileReader(Reader, FileHandler):
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


class FileWriter(Writer, FileHandler):
    """Component factory for file or file-like writers.

    On its own, it can be used to write in a file one line per row that comes into this component. Extending it is
    usually the right way to create more specific file writers (like json, csv, etc.)
    """

    mode = Option(str, default='w+')

    @ContextProcessor
    def lineno(self, context, fs, file):
        lineno = ValueHolder(0)
        yield lineno

    def write(self, fs, file, lineno, line):
        """
        Write a row on the next line of opened file in context.
        """
        self._write_line(file, (self.eol if lineno.value else '') + line)
        lineno += 1
        return NOT_MODIFIED

    def _write_line(self, file, line):
        return file.write(line)
