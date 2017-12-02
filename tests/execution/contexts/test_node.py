from unittest.mock import MagicMock

import pytest

from bonobo import Graph
from bonobo.constants import EMPTY, NOT_MODIFIED, INHERIT
from bonobo.execution.contexts.node import NodeExecutionContext, split_token
from bonobo.execution.strategies import NaiveStrategy
from bonobo.util.testing import BufferingNodeExecutionContext, BufferingGraphExecutionContext


def test_node_string():
    def f():
        return 'foo'

    with BufferingNodeExecutionContext(f) as context:
        context.write_sync(EMPTY)
        output = context.get_buffer()

        assert len(output) == 1
        assert output[0] == ('foo', )

    def g():
        yield 'foo'
        yield 'bar'

    with BufferingNodeExecutionContext(g) as context:
        context.write_sync(EMPTY)
        output = context.get_buffer()

        assert len(output) == 2
        assert output[0] == ('foo', )
        assert output[1] == ('bar', )


def test_node_bytes():
    def f():
        return b'foo'

    with BufferingNodeExecutionContext(f) as context:
        context.write_sync(EMPTY)

        output = context.get_buffer()
        assert len(output) == 1
        assert output[0] == (b'foo', )

    def g():
        yield b'foo'
        yield b'bar'

    with BufferingNodeExecutionContext(g) as context:
        context.write_sync(EMPTY)
        output = context.get_buffer()

        assert len(output) == 2
        assert output[0] == (b'foo', )
        assert output[1] == (b'bar', )


def test_node_dict():
    def f():
        return {'id': 1, 'name': 'foo'}

    with BufferingNodeExecutionContext(f) as context:
        context.write_sync(EMPTY)
        output = context.get_buffer()
        assert len(output) == 1
        assert output[0] == ({'id': 1, 'name': 'foo'}, )

    def g():
        yield {'id': 1, 'name': 'foo'}
        yield {'id': 2, 'name': 'bar'}

    with BufferingNodeExecutionContext(g) as context:
        context.write_sync(EMPTY)
        output = context.get_buffer()
        assert len(output) == 2
        assert output[0] == ({'id': 1, 'name': 'foo'}, )
        assert output[1] == ({'id': 2, 'name': 'bar'}, )


def test_node_dict_chained():
    strategy = NaiveStrategy(GraphExecutionContextType=BufferingGraphExecutionContext)

    def f():
        return {'id': 1, 'name': 'foo'}

    def uppercase_name(values):
        return {**values, 'name': values['name'].upper()}

    graph = Graph(f, uppercase_name)
    context = strategy.execute(graph)
    output = context.get_buffer()

    assert len(output) == 1
    assert output[0] == ({'id': 1, 'name': 'FOO'}, )

    def g():
        yield {'id': 1, 'name': 'foo'}
        yield {'id': 2, 'name': 'bar'}

    graph = Graph(g, uppercase_name)
    context = strategy.execute(graph)
    output = context.get_buffer()

    assert len(output) == 2
    assert output[0] == ({'id': 1, 'name': 'FOO'}, )
    assert output[1] == ({'id': 2, 'name': 'BAR'}, )


def test_node_tuple():
    def f():
        return 'foo', 'bar'

    with BufferingNodeExecutionContext(f) as context:
        context.write_sync(EMPTY)
        output = context.get_buffer()

        assert len(output) == 1
        assert output[0] == ('foo', 'bar')

    def g():
        yield 'foo', 'bar'
        yield 'foo', 'baz'

    with BufferingNodeExecutionContext(g) as context:
        context.write_sync(EMPTY)
        output = context.get_buffer()

        assert len(output) == 2
        assert output[0] == ('foo', 'bar')
        assert output[1] == ('foo', 'baz')


def test_node_tuple_chained():
    strategy = NaiveStrategy(GraphExecutionContextType=BufferingGraphExecutionContext)

    def uppercase(*args):
        return tuple(map(str.upper, args))

    def f():
        return 'foo', 'bar'

    graph = Graph(f, uppercase)
    context = strategy.execute(graph)
    output = context.get_buffer()

    assert len(output) == 1
    assert output[0] == ('FOO', 'BAR')

    def g():
        yield 'foo', 'bar'
        yield 'foo', 'baz'

    graph = Graph(g, uppercase)
    context = strategy.execute(graph)
    output = context.get_buffer()

    assert len(output) == 2
    assert output[0] == ('FOO', 'BAR')
    assert output[1] == ('FOO', 'BAZ')


def test_node_tuple_dict():
    def f():
        return 'foo', 'bar', {'id': 1}

    with BufferingNodeExecutionContext(f) as context:
        context.write_sync(EMPTY)
        output = context.get_buffer()

        assert len(output) == 1
        assert output[0] == ('foo', 'bar', {'id': 1})

    def g():
        yield 'foo', 'bar', {'id': 1}
        yield 'foo', 'baz', {'id': 2}

    with BufferingNodeExecutionContext(g) as context:
        context.write_sync(EMPTY)
        output = context.get_buffer()

        assert len(output) == 2
        assert output[0] == ('foo', 'bar', {'id': 1})
        assert output[1] == ('foo', 'baz', {'id': 2})


def test_node_lifecycle_natural():
    func = MagicMock(spec=object())

    ctx = NodeExecutionContext(func)
    assert not any((ctx.started, ctx.stopped, ctx.killed, ctx.alive))

    # cannot stop before start
    with pytest.raises(RuntimeError):
        ctx.stop()
    assert not any((ctx.started, ctx.stopped, ctx.killed, ctx.alive))

    # turn the key
    ctx.start()
    assert all((ctx.started, ctx.alive)) and not any((ctx.stopped, ctx.killed))

    ctx.stop()
    assert all((ctx.started, ctx.stopped)) and not any((ctx.alive, ctx.killed))


def test_node_lifecycle_with_kill():
    func = MagicMock(spec=object())

    ctx = NodeExecutionContext(func)
    assert not any((ctx.started, ctx.stopped, ctx.killed, ctx.alive))

    # cannot kill before start
    with pytest.raises(RuntimeError):
        ctx.kill()
    assert not any((ctx.started, ctx.stopped, ctx.killed, ctx.alive))

    # turn the key
    ctx.start()
    assert all((ctx.started, ctx.alive)) and not any((ctx.stopped, ctx.killed))

    ctx.kill()
    assert all((ctx.started, ctx.killed, ctx.alive)) and not ctx.stopped

    ctx.stop()
    assert all((ctx.started, ctx.killed, ctx.stopped)) and not ctx.alive


def test_split_token():
    assert split_token(('foo', 'bar')) == (set(), ('foo', 'bar'))
    assert split_token(()) == (set(), ())
    assert split_token('') == (set(), ('', ))


def test_split_token_duplicate():
    with pytest.raises(ValueError):
        split_token((NOT_MODIFIED, NOT_MODIFIED))
    with pytest.raises(ValueError):
        split_token((INHERIT, INHERIT))
    with pytest.raises(ValueError):
        split_token((INHERIT, NOT_MODIFIED, INHERIT))


def test_split_token_not_modified():
    with pytest.raises(ValueError):
        split_token((NOT_MODIFIED, 'foo', 'bar'))
    with pytest.raises(ValueError):
        split_token((NOT_MODIFIED, INHERIT))
    with pytest.raises(ValueError):
        split_token((INHERIT, NOT_MODIFIED))
    assert split_token(NOT_MODIFIED) == ({NOT_MODIFIED}, ())
    assert split_token((NOT_MODIFIED, )) == ({NOT_MODIFIED}, ())


def test_split_token_inherit():
    assert split_token(INHERIT) == ({INHERIT}, ())
    assert split_token((INHERIT, )) == ({INHERIT}, ())
    assert split_token((INHERIT, 'foo', 'bar')) == ({INHERIT}, ('foo', 'bar'))
