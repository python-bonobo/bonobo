from bonobo.util.lifecycle import with_context

__all__ = ['FileWriter', ]


@with_context
class FileWriter:
    # XXX TODO implement @with_context like this ? Pros and cons ?
    class Meta:
        contextual = True

    def __init__(self, path_or_buf, eol='\n'):
        self.path_or_buf = path_or_buf
        self.eol = eol

    def initialize(self, ctx):
        """ todo add lock file ? optional maybe ? """
        assert not hasattr(ctx, 'fp'), 'One at a time, baby.'
        ctx.fp = open(self.path_or_buf, 'w+')
        ctx.first = True

    def write(self, fp, line, prefix=''):
        fp.write(prefix + line)

    def __call__(self, ctx, row):
        if ctx.first:
            prefix, ctx.first = '', False
        else:
            prefix = self.eol

        self.write(ctx.fp, row, prefix=prefix)

    def finalize(self, ctx):
        ctx.fp.close()
        del ctx.fp, ctx.first
