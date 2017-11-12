import json

from bonobo.config.options import RemovedOption
from bonobo.config.processors import ContextProcessor
from bonobo.constants import NOT_MODIFIED
from bonobo.nodes.io.base import FileHandler
from bonobo.nodes.io.file import FileReader, FileWriter
from bonobo.structs.bags import Bag


class JsonHandler(FileHandler):
    eol = ',\n'
    prefix, suffix = '[', ']'
    ioformat = RemovedOption(positional=False, value='kwargs')


class JsonReader(FileReader, JsonHandler):
    loader = staticmethod(json.load)

    def read(self, fs, file):
        for line in self.loader(file):
            yield line


class JsonDictItemsReader(JsonReader):
    def read(self, fs, file):
        for line in self.loader(file).items():
            yield Bag(*line)


class JsonWriter(FileWriter, JsonHandler):
    @ContextProcessor
    def envelope(self, context, fs, file, lineno):
        file.write(self.prefix)
        yield
        file.write(self.suffix)

    def write(self, fs, file, lineno, arg0=None, **kwargs):
        """
        Write a json row on the next line of file pointed by ctx.file.

        :param ctx:
        :param row:
        """
        row = _getrow(arg0, kwargs)
        self._write_line(file, (self.eol if lineno.value else '') + json.dumps(row))
        lineno += 1
        return NOT_MODIFIED


class LdjsonReader(FileReader):
    """Read a stream of JSON objects, one object per line."""
    loader = staticmethod(json.loads)

    def read(self, fs, file):
        for line in file:
            yield self.loader(line)


class LdjsonWriter(FileWriter):
    """Write a stream of JSON objects, one object per line."""

    def write(self, fs, file, lineno, arg0=None, **kwargs):
        row = _getrow(arg0, kwargs)
        file.write(json.dumps(row) + '\n')
        lineno += 1  # class-level variable
        return NOT_MODIFIED


def _getrow(arg0, kwargs):
    if len(kwargs):
        assert arg0 is None, 'Got both positional and keyword arguments, I recommend using keyword arguments.'
        return kwargs

    if arg0 is not None:
        return arg0

    return kwargs
