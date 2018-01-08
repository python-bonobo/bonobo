class Token:
    """Factory for signal oriented queue messages or other token types."""

    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return '<{}>'.format(self.__name__)


BEGIN = Token('Begin')
END = Token('End')


class Flag(Token):
    must_be_first = False
    must_be_last = False
    allows_data = True


INHERIT = Flag('Inherit')
NOT_MODIFIED = Flag('NotModified')
NOT_MODIFIED.must_be_first = True
NOT_MODIFIED.must_be_last = True
NOT_MODIFIED.allows_data = False

EMPTY = tuple()

TICK_PERIOD = 0.2
