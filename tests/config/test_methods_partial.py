from unittest.mock import MagicMock

from bonobo.config import Configurable, ContextProcessor, Method, Option
from bonobo.util.inspect import inspect_node


class Bobby(Configurable):
    handler = Method()
    handler2 = Method()
    foo = Option(positional=True)
    bar = Option(required=False)

    @ContextProcessor
    def think(self, context):
        yield "different"

    def __call__(self, think, *args, **kwargs):
        self.handler("1", *args, **kwargs)
        self.handler2("2", *args, **kwargs)


def test_partial():
    C = Bobby

    # inspect the configurable class
    with inspect_node(C) as ci:
        assert ci.type == Bobby
        assert not ci.instance
        assert len(ci.options) == 4
        assert len(ci.processors) == 1
        assert not ci.partial

    # instanciate a partial instance ...
    f1 = MagicMock()
    C = C(f1)

    with inspect_node(C) as ci:
        assert ci.type == Bobby
        assert not ci.instance
        assert len(ci.options) == 4
        assert len(ci.processors) == 1
        assert ci.partial
        assert ci.partial[0] == (f1,)
        assert not len(ci.partial[1])

    # instanciate a more complete partial instance ...
    f2 = MagicMock()
    C = C(f2)

    with inspect_node(C) as ci:
        assert ci.type == Bobby
        assert not ci.instance
        assert len(ci.options) == 4
        assert len(ci.processors) == 1
        assert ci.partial
        assert ci.partial[0] == (f1, f2)
        assert not len(ci.partial[1])

    c = C("foo")

    with inspect_node(c) as ci:
        assert ci.type == Bobby
        assert ci.instance
        assert len(ci.options) == 4
        assert len(ci.processors) == 1
        assert not ci.partial
