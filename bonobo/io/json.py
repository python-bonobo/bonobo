import json

from .file import FileWriter

__all__ = ['JsonWriter', ]


class JsonHandler:
    eol = ',\n'


class JsonWriter(JsonHandler, FileWriter):
    def initialize(self, ctx):
        print('EOL', self.eol)
        super().initialize(ctx)
        ctx.file.write('[\n')

    def handle(self, ctx, row):
        """
        Write a json row on the next line of file pointed by ctx.file.

        :param ctx:
        :param row:
        """
        return super().handle(ctx, json.dumps(row))

    def finalize(self, ctx):
        ctx.file.write('\n]')
        super().finalize(ctx)
