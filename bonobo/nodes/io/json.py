import json
from collections import OrderedDict

from bonobo.config import Method
from bonobo.config.processors import ContextProcessor, use_context
from bonobo.constants import NOT_MODIFIED
from bonobo.nodes.io.base import FileHandler
from bonobo.nodes.io.file import FileReader, FileWriter


class JsonHandler(FileHandler):
    eol = ',\n'
    prefix, suffix = '[', ']'


class LdjsonHandler(FileHandler):
    eol = '\n'
    prefix, suffix = '', ''


class JsonReader(JsonHandler, FileReader):
    @Method(positional=False)
    def loader(self, file):
        return json.loads(file)

    def read(self, file, *, fs):
        yield from self.loader(file.read())

    __call__ = read


class LdjsonReader(LdjsonHandler, JsonReader):
    """
    Read a stream of line-delimited JSON objects (one object per line).

    Not to be mistaken with JSON-LD (where LD stands for linked data).

    """

    def read(self, file, *, fs):
        yield from map(self.loader, file)

    __call__ = read


@use_context
class JsonWriter(JsonHandler, FileWriter):
    @ContextProcessor
    def envelope(self, context, file, *, fs):
        file.write(self.prefix)
        yield
        file.write(self.suffix)

    def write(self, file, context, *args, fs):
        """
        Write a json row on the next line of file pointed by ctx.file.

        :param ctx:
        :param row:
        """
        context.setdefault('lineno', 0)
        fields = context.get_input_fields()

        if fields:
            prefix = self.eol if context.lineno else ''
            self._write_line(file, prefix + json.dumps(OrderedDict(zip(fields, args))))
            context.lineno += 1
        else:
            for arg in args:
                prefix = self.eol if context.lineno else ''
                self._write_line(file, prefix + json.dumps(arg))
                context.lineno += 1

        return NOT_MODIFIED

    __call__ = write


@use_context
class LdjsonWriter(LdjsonHandler, JsonWriter):
    """
    Write a stream of Line-delimited JSON objects (one object per line).

    Not to be mistaken with JSON-LD (where LD stands for linked data).

    """
