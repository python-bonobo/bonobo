from operator import methodcaller
from unittest import TestCase
from unittest.mock import MagicMock

import pytest

import bonobo
from bonobo.constants import EMPTY, NOT_MODIFIED
from bonobo.util import ValueHolder, ensure_tuple
from bonobo.util.bags import BagType
from bonobo.util.testing import BufferingNodeExecutionContext, ConfigurableNodeTest, StaticNodeTest


class CountTest(StaticNodeTest, TestCase):
    node = bonobo.count

    def test_counter_required(self):
        with pytest.raises(TypeError):
            self.call()

    def test_manual_call(self):
        counter = ValueHolder(0)
        for i in range(3):
            self.call(counter)
        assert counter == 3

    def test_execution(self):
        with self.execute() as context:
            context.write_sync(*([EMPTY] * 42))
        assert context.get_buffer() == [(42,)]


class IdentityTest(StaticNodeTest, TestCase):
    node = bonobo.identity

    def test_basic_call(self):
        assert self.call(42) == 42

    def test_execution(self):
        object_list = [object() for _ in range(42)]
        with self.execute() as context:
            context.write_sync(*object_list)
        assert context.get_buffer() == list(map(ensure_tuple, object_list))


class LimitTest(ConfigurableNodeTest, TestCase):
    @classmethod
    def setUpClass(cls):
        cls.NodeType = bonobo.Limit

    def test_execution_default(self):
        object_list = [object() for _ in range(42)]
        with self.execute() as context:
            context.write_sync(*object_list)

        assert context.get_buffer() == list(map(ensure_tuple, object_list[:10]))

    def test_execution_custom(self):
        object_list = [object() for _ in range(42)]
        with self.execute(21) as context:
            context.write_sync(*object_list)

        assert context.get_buffer() == list(map(ensure_tuple, object_list[:21]))

    def test_manual(self):
        limit = self.NodeType(5)
        buffer = []
        for x in range(10):
            buffer += list(limit(x))
        assert len(buffer) == 5

    def test_underflow(self):
        limit = self.NodeType(10)
        buffer = []
        for x in range(5):
            buffer += list(limit(x))
        assert len(buffer) == 5


def test_tee():
    inner = MagicMock(side_effect=bonobo.identity)
    tee = bonobo.Tee(inner)
    results = []
    for i in range(10):
        results.append(tee("foo"))

    assert results == [NOT_MODIFIED] * 10
    assert len(inner.mock_calls) == 10


def test_noop():
    assert bonobo.noop(1, 2, 3, 4, foo="bar") == NOT_MODIFIED


def test_fixedwindow():
    with BufferingNodeExecutionContext(bonobo.FixedWindow(2)) as context:
        context.write_sync(*range(10))
    assert context.get_buffer() == [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]

    with BufferingNodeExecutionContext(bonobo.FixedWindow(2)) as context:
        context.write_sync(*range(9))
    assert context.get_buffer() == [(0, 1), (2, 3), (4, 5), (6, 7), (8, None)]

    with BufferingNodeExecutionContext(bonobo.FixedWindow(1)) as context:
        context.write_sync(*range(3))
    assert context.get_buffer() == [(0,), (1,), (2,)]


def test_methodcaller():
    with BufferingNodeExecutionContext(methodcaller("swapcase")) as context:
        context.write_sync("aaa", "bBb", "CcC")
    assert context.get_buffer() == list(map(ensure_tuple, ["AAA", "BbB", "cCc"]))

    with BufferingNodeExecutionContext(methodcaller("zfill", 5)) as context:
        context.write_sync("a", "bb", "ccc")
    assert context.get_buffer() == list(map(ensure_tuple, ["0000a", "000bb", "00ccc"]))


MyBag = BagType("MyBag", ["a", "b", "c"])


@pytest.mark.parametrize(
    "input_, key, expected",
    [
        (MyBag(1, 2, 3), True, MyBag(1, 4, 9)),
        (MyBag(1, 2, 3), False, MyBag(1, 2, 3)),
        (MyBag(1, 2, 3), lambda x: x == "c", MyBag(1, 2, 9)),
        ((1, 2, 3), True, (1, 4, 9)),
        ((1, 2, 3), False, (1, 2, 3)),
    ],
)
def test_map_fields(input_, key, expected):
    with BufferingNodeExecutionContext(bonobo.MapFields(lambda x: x ** 2, key)) as context:
        context.write_sync(input_)
    assert context.status == "-"
    [got] = context.get_buffer()
    assert expected == got


def test_map_fields_error():
    with BufferingNodeExecutionContext(bonobo.MapFields(lambda x: x ** 2, lambda x: x == "c")) as context:
        context.write_sync(tuple())
    assert context.status == "!"
    assert context.defunct


def test_set_fields():
    with BufferingNodeExecutionContext(bonobo.SetFields(["x", "y"])) as context:
        context.write_sync((1, 2))

    output = context.get_buffer()
    assert len(output) == 1
    assert output[0]._fields == ("x", "y")
    assert output[0].x == 1
    assert output[0].y == 2
