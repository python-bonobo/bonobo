from unittest.mock import MagicMock

import bonobo
import pytest
from bonobo.config.processors import ContextCurrifier
from bonobo.constants import NOT_MODIFIED


def test_count():
    with pytest.raises(TypeError):
        bonobo.count()

    context = MagicMock()

    currified = ContextCurrifier(bonobo.count)
    currified.setup(context)

    for i in range(42):
        currified()
    currified.teardown()

    assert len(context.method_calls) == 1
    bag = context.send.call_args[0][0]
    assert isinstance(bag, bonobo.Bag)
    assert 0 == len(bag.kwargs)
    assert 1 == len(bag.args)
    assert bag.args[0] == 42


def test_identity():
    assert bonobo.identity(42) == 42


def test_limit():
    limit = bonobo.Limit(2)
    results = []
    for i in range(42):
        results += list(limit())
    assert results == [NOT_MODIFIED] * 2


def test_limit_not_there():
    limit = bonobo.Limit(42)
    results = []
    for i in range(10):
        results += list(limit())
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
