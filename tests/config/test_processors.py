from operator import attrgetter

from bonobo.config import Configurable
from bonobo.config.processors import ContextCurrifier, ContextProcessor, resolve_processors, use_context_processor


class CP1(Configurable):
    @ContextProcessor
    def c(self):
        yield

    @ContextProcessor
    def a(self):
        yield "this is A"

    @ContextProcessor
    def b(self, a):
        yield a.upper()[:-1] + "b"

    def __call__(self, a, b):
        return a, b


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


class CP3(CP2):
    @ContextProcessor
    def c(self):
        pass

    @ContextProcessor
    def b(self):
        pass


def get_all_processors_names(cls):
    return list(map(attrgetter("__name__"), resolve_processors(cls)))


def test_inheritance_and_ordering():
    assert get_all_processors_names(CP1) == ["c", "a", "b"]
    assert get_all_processors_names(CP2) == ["c", "a", "b", "f", "e", "d"]
    assert get_all_processors_names(CP3) == ["c", "a", "b", "f", "e", "d", "c", "b"]


def test_setup_teardown():
    o = CP1()
    stack = ContextCurrifier(o)
    stack.setup()
    assert o(*stack.args) == ("this is A", "THIS IS b")
    stack.teardown()


def test_processors_on_func():
    def cp(context):
        yield context

    @use_context_processor(cp)
    def node(context):
        pass

    assert get_all_processors_names(node) == ["cp"]
