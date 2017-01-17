from operator import attrgetter

from bonobo import contextual, ContextProcessor
from bonobo.context.processors import get_context_processors


@contextual
class CP1:
    @ContextProcessor
    def c(self):
        pass

    @ContextProcessor
    def a(self):
        pass

    @ContextProcessor
    def b(self):
        pass


@contextual
class CP2(CP1):
    @ContextProcessor
    def f(self):
        pass

    @ContextProcessor
    def e(self):
        pass

    @ContextProcessor
    def d(self):
        pass


@contextual
class CP3(CP2):
    @ContextProcessor
    def c(self):
        pass

    @ContextProcessor
    def b(self):
        pass


def get_all_processors_names(cls):
    return list(map(attrgetter('__name__'), get_context_processors(cls)))


def test_inheritance_and_ordering():
    assert get_all_processors_names(CP1) == ['c', 'a', 'b']
    assert get_all_processors_names(CP2) == ['c', 'a', 'b', 'f', 'e', 'd']
    assert get_all_processors_names(CP3) == ['c', 'a', 'b', 'f', 'e', 'd', 'c', 'b']
