from bonobo.config import Configurable, Method, Option
from bonobo.util.inspect import inspect_node


class MethodBasedConfigurable(Configurable):
    handler = Method()
    foo = Option(positional=True)
    bar = Option()

    def __call__(self, *args, **kwargs):
        self.handler(*args, **kwargs)


def test_multiple_wrapper_suppored():
    class TwoMethods(Configurable):
        h1 = Method(required=True)
        h2 = Method(required=True)

    with inspect_node(TwoMethods) as ci:
        assert ci.type == TwoMethods
        assert not ci.instance
        assert len(ci.options) == 2
        assert not len(ci.processors)
        assert not ci.partial

    @TwoMethods
    def OneMethod():
        pass

    with inspect_node(OneMethod) as ci:
        assert ci.type == TwoMethods
        assert not ci.instance
        assert len(ci.options) == 2
        assert not len(ci.processors)
        assert ci.partial

    @OneMethod
    def transformation():
        pass

    with inspect_node(transformation) as ci:
        assert ci.type == TwoMethods
        assert ci.instance
        assert len(ci.options) == 2
        assert not len(ci.processors)
        assert not ci.partial


def test_define_with_decorator():
    calls = []

    def my_handler(*args, **kwargs):
        calls.append((args, kwargs))

    Concrete = MethodBasedConfigurable(my_handler)

    assert callable(Concrete.handler)
    assert Concrete.handler.__func__ == my_handler

    with inspect_node(Concrete) as ci:
        assert ci.type == MethodBasedConfigurable
        assert ci.partial

    t = Concrete("foo", bar="baz")

    assert callable(t.handler)
    assert len(calls) == 0
    t()
    assert len(calls) == 1


def test_late_binding_method_decoration():
    calls = []

    @MethodBasedConfigurable(foo="foo")
    def Concrete(*args, **kwargs):
        calls.append((args, kwargs))

    assert callable(Concrete.handler)
    t = Concrete(bar="baz")

    assert callable(t.handler)
    assert len(calls) == 0
    t()
    assert len(calls) == 1


def test_define_with_argument():
    calls = []

    def concrete_handler(*args, **kwargs):
        calls.append((args, kwargs))

    t = MethodBasedConfigurable(concrete_handler, "foo", bar="baz")
    assert callable(t.handler)
    assert len(calls) == 0
    t()
    assert len(calls) == 1


def test_define_with_inheritance():
    calls = []

    class Inheriting(MethodBasedConfigurable):
        def handler(self, *args, **kwargs):
            calls.append((args, kwargs))

    t = Inheriting("foo", bar="baz")
    assert callable(t.handler)
    assert len(calls) == 0
    t()
    assert len(calls) == 1


def test_inheritance_then_decorate():
    calls = []

    class Inheriting(MethodBasedConfigurable):
        pass

    @Inheriting
    def Concrete(*args, **kwargs):
        calls.append((args, kwargs))

    assert callable(Concrete.handler)
    t = Concrete("foo", bar="baz")
    assert callable(t.handler)
    assert len(calls) == 0
    t()
    assert len(calls) == 1
