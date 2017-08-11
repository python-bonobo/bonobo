import json

from bonobo.config.processors import ContextProcessor
from bonobo.constants import NOT_MODIFIED
from bonobo.nodes.io.base import FileHandler, IOFormatEnabled
from bonobo.nodes.io.file import FileReader, FileWriter


class JsonHandler(FileHandler):
    eol = ',\n'
    prefix, suffix = '[', ']'


class JsonReader(IOFormatEnabled, FileReader, JsonHandler):
    loader = staticmethod(json.load)

    def read(self, fs, file):
        for line in self.loader(file):
            yield self.get_output(line)


class JsonWriter(IOFormatEnabled, FileWriter, JsonHandler):
    @ContextProcessor
    def envelope(self, context, fs, file, lineno):
        file.write(self.prefix)
        yield
        file.write(self.suffix)

    def write(self, fs, file, lineno, *args, **kwargs):
        """
        Write a json row on the next line of file pointed by ctx.file.

        :param ctx:
        :param row:
        """
        row = self.get_input(*args, **kwargs)
        self._write_line(file, (self.eol if lineno.value else '') + json.dumps(row))
        lineno += 1
        return NOT_MODIFIED
