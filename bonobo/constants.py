class Token:
    """Factory for signal oriented queue messages or other token types."""

    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return '<{}>'.format(self.__name__)


BEGIN = Token('Begin')
END = Token('End')

INHERIT_INPUT = Token('InheritInput')
LOOPBACK = Token('Loopback')
NOT_MODIFIED = Token('NotModified')

EMPTY = tuple()

TICK_PERIOD = 0.2
