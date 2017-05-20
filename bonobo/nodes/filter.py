from bonobo.constants import NOT_MODIFIED

from bonobo.config import Configurable, Method


class Filter(Configurable):
    """Filter out hashes from the stream depending on the :attr:`filter` callable return value, when called with the
    current hash as parameter.

    Can be used as a decorator on a filter callable.

    .. attribute:: filter

        A callable used to filter lines.
        
        If the callable returns a true-ish value, the input will be passed unmodified to the next items.
        
        Otherwise, it'll be burnt.

    """

    filter = Method()

    def call(self, *args, **kwargs):
        if self.filter(*args, **kwargs):
            return NOT_MODIFIED
