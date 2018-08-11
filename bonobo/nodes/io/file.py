from bonobo.config import ContextProcessor, Option, use_context
from bonobo.constants import NOT_MODIFIED
from bonobo.errors import UnrecoverableError
from bonobo.nodes.io.base import FileHandler, Reader, Writer
from bonobo.util import ensure_tuple


class FileReader(Reader, FileHandler):
    """Component factory for file-like readers.

    On its own, it can be used to read a file and yield one row per line, trimming the "eol" character at the end if
    present. Extending it is usually the right way to create more specific file readers (like json, csv, etc.)
    """

    mode = Option(
        str,
        default='r',
        __doc__='''
        What mode to use for open() call.
    ''',
    )  # type: str

    output_fields = Option(
        ensure_tuple,
        required=False,
        __doc__='''
        Specify the field names of output lines.
        Mutually exclusive with "output_type".
    ''',
    )
    output_type = Option(
        required=False,
        __doc__='''
        Specify the type of output lines.
        Mutually exclusive with "output_fields".
    ''',
    )

    @ContextProcessor
    def output(self, context, *args, **kwargs):
        """
        Allow all readers to use eventually use output_fields XOR output_type options.

        """

        output_fields = self.output_fields
        output_type = self.output_type

        if output_fields and output_type:
            raise UnrecoverableError('Cannot specify both output_fields and output_type option.')

        if self.output_type:
            context.set_output_type(self.output_type)

        if self.output_fields:
            context.set_output_fields(self.output_fields)

        yield

    def read(self, file, *, fs):
        """
        Write a row on the next line of given file.
        Prefix is used for newlines.
        """
        for line in file:
            yield line.rstrip(self.eol)

    __call__ = read


@use_context
class FileWriter(Writer, FileHandler):
    """Component factory for file or file-like writers.

    On its own, it can be used to write in a file one line per row that comes into this component. Extending it is
    usually the right way to create more specific file writers (like json, csv, etc.)
    """

    mode = Option(
        str,
        default='w+',
        __doc__='''
        What mode to use for open() call.
    ''',
    )  # type: str

    def write(self, file, context, line, *, fs):
        """
        Write a row on the next line of opened file in context.
        """
        context.setdefault('lineno', 0)
        self._write_line(file, (self.eol if context.lineno else '') + line)
        context.lineno += 1
        return NOT_MODIFIED

    def _write_line(self, file, line):
        return file.write(line)

    __call__ = write
