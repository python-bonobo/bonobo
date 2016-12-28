import json

from .file import FileWriter, FileReader

__all__ = ['JsonWriter', ]


class JsonHandler:
    eol = ',\n'


class JsonReader(JsonHandler, FileReader):
    def read(self, ctx):
        for line in json.load(ctx.file):
            yield line


class JsonWriter(JsonHandler, FileWriter):
    def initialize(self, ctx):
        super().initialize(ctx)
        ctx.file.write('[\n')

    def write(self, ctx, row):
        """
        Write a json row on the next line of file pointed by ctx.file.

        :param ctx:
        :param row:
        """
        return super().write(ctx, json.dumps(row))

    def finalize(self, ctx):
        ctx.file.write('\n]')
        super().finalize(ctx)
