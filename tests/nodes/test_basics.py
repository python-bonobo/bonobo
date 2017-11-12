from operator import methodcaller
from unittest.mock import MagicMock

import pytest

import bonobo
from bonobo.config.processors import ContextCurrifier
from bonobo.constants import NOT_MODIFIED
from bonobo.util.testing import BufferingNodeExecutionContext


def test_count():
    with pytest.raises(TypeError):
        bonobo.count()

    context = MagicMock()

    with ContextCurrifier(bonobo.count).as_contextmanager(context) as stack:
        for i in range(42):
            stack()

    assert len(context.method_calls) == 1
    bag = context.send.call_args[0][0]
    assert isinstance(bag, bonobo.Bag)
    assert 0 == len(bag.kwargs)
    assert 1 == len(bag.args)
    assert bag.args[0] == 42


def test_identity():
    assert bonobo.identity(42) == 42


def test_limit():
    context, results = MagicMock(), []

    with ContextCurrifier(bonobo.Limit(2)).as_contextmanager(context) as stack:
        for i in range(42):
            results += list(stack())

    assert results == [NOT_MODIFIED] * 2


def test_limit_not_there():
    context, results = MagicMock(), []

    with ContextCurrifier(bonobo.Limit(42)).as_contextmanager(context) as stack:
        for i in range(10):
            results += list(stack())

    assert results == [NOT_MODIFIED] * 10


def test_limit_default():
    context, results = MagicMock(), []

    with ContextCurrifier(bonobo.Limit()).as_contextmanager(context) as stack:
        for i in range(20):
            results += list(stack())

    assert results == [NOT_MODIFIED] * 10


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


def test_update():
    with BufferingNodeExecutionContext(bonobo.Update('a', k=True)) as context:
        context.write_sync('a', ('a', {'b': 1}), ('b', {'k': False}))
    assert context.get_buffer() == [
        bonobo.Bag('a', 'a', k=True),
        bonobo.Bag('a', 'a', b=1, k=True),
        bonobo.Bag('b', 'a', k=True),
    ]
    assert context.name == "Update('a', k=True)"


def test_fixedwindow():
    with BufferingNodeExecutionContext(bonobo.FixedWindow(2)) as context:
        context.write_sync(*range(10))
    assert context.get_buffer() == [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

    with BufferingNodeExecutionContext(bonobo.FixedWindow(2)) as context:
        context.write_sync(*range(9))
    assert context.get_buffer() == [[0, 1], [2, 3], [4, 5], [6, 7], [8]]

    with BufferingNodeExecutionContext(bonobo.FixedWindow(1)) as context:
        context.write_sync(*range(3))
    assert context.get_buffer() == [[0], [1], [2]]


def test_methodcaller():
    with BufferingNodeExecutionContext(methodcaller('swapcase')) as context:
        context.write_sync('aaa', 'bBb', 'CcC')
    assert context.get_buffer() == ['AAA', 'BbB', 'cCc']

    with BufferingNodeExecutionContext(methodcaller('zfill', 5)) as context:
        context.write_sync('a', 'bb', 'ccc')
    assert context.get_buffer() == ['0000a', '000bb', '00ccc']
