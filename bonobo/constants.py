"""
.. data:: BEGIN

    **BEGIN** token marks the entrypoint of graphs, and all extractors will be connected to this node.

    Without this, it would be impossible for an execution to actually start anything, as it's the marker that tells
    |bonobo| which node to actually call when the execution starts.

.. data:: NOT_MODIFIED

    **NOT_MODIFIED** is a special value you can return or yield from a transformation to tell bonobo to reuse
    the input data as output.

    As a convention, all loaders should return this, so loaders can be chained.

.. data:: EMPTY

    Shortcut for "empty tuple". It's often much more clear to write (especially in a test) `write(EMPTY)` than
    `write(())`, although strictly equivalent.


"""


class Token:
    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return '<{}>'.format(self.__name__)


class Flag(Token):
    must_be_first = False
    must_be_last = False
    allows_data = True


BEGIN = Token('Begin')
END = Token('End')

INHERIT = Flag('Inherit')
NOT_MODIFIED = Flag('NotModified')
NOT_MODIFIED.must_be_first = True
NOT_MODIFIED.must_be_last = True
NOT_MODIFIED.allows_data = False

EMPTY = tuple()

TICK_PERIOD = 0.2
