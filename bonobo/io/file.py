from bonobo.util.lifecycle import with_context

__all__ = [
    'FileHandler',
    'FileReader',
    'FileWriter',
]


@with_context
class FileHandler:
    """
    Abstract component factory for file-related components.

    """

    eol = '\n'
    mode = None

    def __init__(self, path_or_buf, eol=None):
        self.path_or_buf = path_or_buf
        self.eol = eol or self.eol

    def open(self):
        return open(self.path_or_buf, self.mode)

    def close(self, fp):
        """
        :param file fp:
        """
        fp.close()

    def initialize(self, ctx):
        """
        Initialize a
        :param ctx:
        :return:
        """
        assert not hasattr(ctx, 'file'), 'A file pointer is already in the context... I do not know what to say...'
        ctx.file = self.open()

    def finalize(self, ctx):
        self.close(ctx.file)
        del ctx.file


class Reader(FileHandler):
    def __call__(self, ctx):
        yield from self.read(ctx)

    def read(self, ctx):
        raise NotImplementedError('Abstract.')


class Writer(FileHandler):
    def __call__(self, ctx, row):
        return self.write(ctx, row)

    def write(self, ctx, row):
        raise NotImplementedError('Abstract.')


class FileReader(Reader):
    """
    Component factory for file-like readers.

    On its own, it can be used to read a file and yield one row per line, trimming the "eol" character at the end if
    present. Extending it is usually the right way to create more specific file readers (like json, csv, etc.)

    """

    mode = 'r'

    def read(self, ctx):
        """
        Write a row on the next line of file pointed by `ctx.file`.
        Prefix is used for newlines.

        :param ctx:
        :param row:
        """
        for line in ctx.file:
            yield line.rstrip(self.eol)


class FileWriter(Writer):
    """
    Component factory for file or file-like writers.

    On its own, it can be used to write in a file one line per row that comes into this component. Extending it is
    usually the right way to create more specific file writers (like json, csv, etc.)

    """

    mode = 'w+'

    def initialize(self, ctx):
        super().initialize(ctx)
        ctx.line = 0

    def write(self, ctx, row):
        """
        Write a row on the next line of opened file in context.

        :param file fp:
        :param str row:
        :param str prefix:
        """
        self._write_line(ctx.file, (self.eol if ctx.line else '') + row)
        ctx.line += 1

    def _write_line(self, fp, line):
        return fp.write(line)

    def finalize(self, ctx):
        del ctx.line
        super().finalize(ctx)
