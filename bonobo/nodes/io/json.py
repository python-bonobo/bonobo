import json

from bonobo.config.processors import ContextProcessor
from .file import FileWriter, FileReader

__all__ = [
    'JsonWriter',
]


class JsonHandler():
    eol = ',\n'
    prefix, suffix = '[', ']'


class JsonReader(JsonHandler, FileReader):
    loader = staticmethod(json.load)

    def read(self, fs, file):
        for line in self.loader(file):
            yield line


class JsonWriter(JsonHandler, FileWriter):
    @ContextProcessor
    def envelope(self, context, fs, file, lineno):
        file.write(self.prefix)
        yield
        file.write(self.suffix)

    def write(self, fs, file, lineno, row):
        """
        Write a json row on the next line of file pointed by ctx.file.

        :param ctx:
        :param row:
        """
        return super().write(fs, file, lineno, json.dumps(row))
