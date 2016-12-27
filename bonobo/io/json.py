import json

from bonobo.util.lifecycle import with_context

__all__ = [
    'from_json',
    'to_json',
]


@with_context
class JsonWriter:
    def __init__(self, path_or_buf):
        self.path_or_buf = path_or_buf

    def initialize(self, ctx):
        assert not hasattr(ctx, 'fp'), 'One at a time, baby.'
        ctx.fp = open(self.path_or_buf, 'w+')
        ctx.fp.write('[\n')
        ctx.first = True

    def __call__(self, ctx, row):
        if ctx.first:
            prefix = ''
            ctx.first = False
        else:
            prefix = ',\n'
        ctx.fp.write(prefix + json.dumps(row))

    def finalize(self, ctx):
        ctx.fp.write('\n]')
        ctx.fp.close()
        del ctx.fp, ctx.first


def from_json(path_or_buf):
    pass


to_json = JsonWriter
