import pytest

from bonobo.config import Configurable, Method, Option
from bonobo.errors import ConfigurationError


class MethodBasedConfigurable(Configurable):
    handler = Method()
    foo = Option(positional=True)
    bar = Option()

    def call(self, *args, **kwargs):
        self.handler(*args, **kwargs)


def test_one_wrapper_only():
    with pytest.raises(ConfigurationError):

        class TwoMethods(Configurable):
            h1 = Method()
            h2 = Method()


def test_define_with_decorator():
    calls = []

    @MethodBasedConfigurable
    def Concrete(self, *args, **kwargs):
        calls.append((args, kwargs, ))

    print('handler', Concrete.handler)

    assert callable(Concrete.handler)
    t = Concrete('foo', bar='baz')

    assert callable(t.handler)
    assert len(calls) == 0
    t()
    assert len(calls) == 1


def test_define_with_argument():
    calls = []

    def concrete_handler(*args, **kwargs):
        calls.append((args, kwargs, ))

    t = MethodBasedConfigurable('foo', bar='baz', handler=concrete_handler)
    assert callable(t.handler)
    assert len(calls) == 0
    t()
    assert len(calls) == 1


def test_define_with_inheritance():
    calls = []

    class Inheriting(MethodBasedConfigurable):
        def handler(self, *args, **kwargs):
            calls.append((args, kwargs, ))

    t = Inheriting('foo', bar='baz')
    assert callable(t.handler)
    assert len(calls) == 0
    t()
    assert len(calls) == 1


def test_inheritance_then_decorate():
    calls = []

    class Inheriting(MethodBasedConfigurable):
        pass

    @Inheriting
    def Concrete(self, *args, **kwargs):
        calls.append((args, kwargs, ))

    assert callable(Concrete.handler)
    t = Concrete('foo', bar='baz')
    assert callable(t.handler)
    assert len(calls) == 0
    t()
    assert len(calls) == 1
