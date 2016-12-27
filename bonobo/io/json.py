import json

from .file import FileWriter
from bonobo.util.lifecycle import with_context

__all__ = ['JsonFileWriter', ]


@with_context
class JsonFileWriter(FileWriter):
    def __init__(self, path_or_buf):
        super().__init__(path_or_buf, eol=',\n')

    def initialize(self, ctx):
        super().initialize(ctx)
        ctx.fp.write('[\n')

    def write(self, fp, line, prefix=''):
        fp.write(prefix + json.dumps(line))

    def finalize(self, ctx):
        ctx.fp.write('\n]')
        super().finalize(ctx)
