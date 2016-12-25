import json

from bonobo.util.lifecycle import with_context, set_initializer, set_finalizer

__all__ = ['to_json', ]


def to_json(path_or_buf):
    # todo different cases + documentation
    # case 1: path_or_buf is str, we consider it filename, open and write
    # case 2: pob is None, json should be yielded
    # case 3: pob is stream, filelike, write, gogog.

    @with_context
    def _to_json(ctx, row):
        if ctx.first:
            prefix = ''
            ctx.first = False
        else:
            prefix = ',\n'
        ctx.fp.write(prefix + json.dumps(row))

    @set_initializer(_to_json)
    def _to_json_initialize(ctx):
        assert not hasattr(ctx, 'fp'), 'One at a time, baby.'
        ctx.fp = open(path_or_buf, 'w+')
        ctx.fp.write('[\n')
        ctx.first = True

    @set_finalizer(_to_json)
    def _to_json_finalize(ctx):
        ctx.fp.write('\n]')
        ctx.fp.close()
        del ctx.fp, ctx.first

    _to_json.__name__ = 'to_json'

    return _to_json
