from bonobo.structs.tokens import Flag

F_INHERIT = Flag("Inherit")

F_NOT_MODIFIED = Flag("NotModified")
F_NOT_MODIFIED.must_be_first = True
F_NOT_MODIFIED.must_be_last = True
F_NOT_MODIFIED.allows_data = False


class Envelope:
    def __init__(self, content, *, flags=None, **options):
        self._content = content
        self._flags = set(flags or ())
        self._options = options

    def unfold(self):
        return self._content, self._flags, self._options


class AppendingEnvelope(Envelope):
    def __init__(self, content, **options):
        super().__init__(content, flags={F_INHERIT}, **options)


class UnchangedEnvelope(Envelope):
    def __init__(self, **options):
        super().__init__(None, flags={F_NOT_MODIFIED}, **options)


def isenvelope(mixed):
    return isinstance(mixed, Envelope)
