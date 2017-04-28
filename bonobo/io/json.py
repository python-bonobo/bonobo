import json

from bonobo.config.processors import ContextProcessor, contextual
from .file import FileWriter, FileReader

__all__ = [
    'JsonWriter',
]


class JsonHandler:
    eol = ',\n'


class JsonReader(JsonHandler, FileReader):
    loader = staticmethod(json.load)

    def read(self, fs, file):
        for line in self.loader(file):
            yield line


@contextual
class JsonWriter(JsonHandler, FileWriter):
    @ContextProcessor
    def envelope(self, context, fs, file, lineno):
        file.write('[\n')
        yield
        file.write('\n]')

    def write(self, fs, file, lineno, row):
        """
        Write a json row on the next line of file pointed by ctx.file.

        :param ctx:
        :param row:
        """
        return super().write(fs, file, lineno, json.dumps(row))
