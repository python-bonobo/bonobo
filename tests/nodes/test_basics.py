from operator import methodcaller
from unittest import TestCase
from unittest.mock import MagicMock

import pytest

import bonobo
from bonobo.constants import NOT_MODIFIED, EMPTY
from bonobo.util import ensure_tuple, ValueHolder
from bonobo.util.testing import BufferingNodeExecutionContext, StaticNodeTest, ConfigurableNodeTest


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
        assert context.get_buffer() == [(42, )]


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
        results.append(tee('foo'))

    assert results == [NOT_MODIFIED] * 10
    assert len(inner.mock_calls) == 10


def test_noop():
    assert bonobo.noop(1, 2, 3, 4, foo='bar') == NOT_MODIFIED


def test_fixedwindow():
    with BufferingNodeExecutionContext(bonobo.FixedWindow(2)) as context:
        context.write_sync(*range(10))
    assert context.get_buffer() == [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]

    with BufferingNodeExecutionContext(bonobo.FixedWindow(2)) as context:
        context.write_sync(*range(9))
    assert context.get_buffer() == [(0, 1), (2, 3), (4, 5), (6, 7), (
        8,
        None,
    )]

    with BufferingNodeExecutionContext(bonobo.FixedWindow(2, pad=False)) as context:
        context.write_sync(*range(9))
    assert context.get_buffer() == [(0, 1), (2, 3), (4, 5), (6, 7), (8, )]

    with BufferingNodeExecutionContext(bonobo.FixedWindow(2, pad_value=-1)) as context:
        context.write_sync(*range(9))
    assert context.get_buffer() == [(0, 1), (2, 3), (4, 5), (6, 7), (8, -1)]


def test_methodcaller():
    with BufferingNodeExecutionContext(methodcaller('swapcase')) as context:
        context.write_sync('aaa', 'bBb', 'CcC')
    assert context.get_buffer() == list(map(ensure_tuple, ['AAA', 'BbB', 'cCc']))

    with BufferingNodeExecutionContext(methodcaller('zfill', 5)) as context:
        context.write_sync('a', 'bb', 'ccc')
    assert context.get_buffer() == list(map(ensure_tuple, ['0000a', '000bb', '00ccc']))
