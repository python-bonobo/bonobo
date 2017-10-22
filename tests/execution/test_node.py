from bonobo import Bag, Graph
from bonobo.strategies import NaiveStrategy
from bonobo.util.testing import BufferingNodeExecutionContext, BufferingGraphExecutionContext


def test_node_string():
    def f():
        return 'foo'

    with BufferingNodeExecutionContext(f) as context:
        context.write_sync(Bag())
        output = context.get_buffer()

        assert len(output) == 1
        assert output[0] == (('foo', ), {})

    def g():
        yield 'foo'
        yield 'bar'

    with BufferingNodeExecutionContext(g) as context:
        context.write_sync(Bag())
        output = context.get_buffer()

        assert len(output) == 2
        assert output[0] == (('foo', ), {})
        assert output[1] == (('bar', ), {})


def test_node_bytes():
    def f():
        return b'foo'

    with BufferingNodeExecutionContext(f) as context:
        context.write_sync(Bag())

        output = context.get_buffer()
        assert len(output) == 1
        assert output[0] == ((b'foo', ), {})

    def g():
        yield b'foo'
        yield b'bar'

    with BufferingNodeExecutionContext(g) as context:
        context.write_sync(Bag())
        output = context.get_buffer()

        assert len(output) == 2
        assert output[0] == ((b'foo', ), {})
        assert output[1] == ((b'bar', ), {})


def test_node_dict():
    def f():
        return {'id': 1, 'name': 'foo'}

    with BufferingNodeExecutionContext(f) as context:
        context.write_sync(Bag())
        output = context.get_buffer()

        assert len(output) == 1
        assert output[0] == {'id': 1, 'name': 'foo'}

    def g():
        yield {'id': 1, 'name': 'foo'}
        yield {'id': 2, 'name': 'bar'}

    with BufferingNodeExecutionContext(g) as context:
        context.write_sync(Bag())
        output = context.get_buffer()

        assert len(output) == 2
        assert output[0] == {'id': 1, 'name': 'foo'}
        assert output[1] == {'id': 2, 'name': 'bar'}


def test_node_dict_chained():
    strategy = NaiveStrategy(GraphExecutionContextType=BufferingGraphExecutionContext)

    def uppercase_name(**kwargs):
        return {**kwargs, 'name': kwargs['name'].upper()}

    def f():
        return {'id': 1, 'name': 'foo'}

    graph = Graph(f, uppercase_name)
    context = strategy.execute(graph)
    output = context.get_buffer()

    assert len(output) == 1
    assert output[0] == {'id': 1, 'name': 'FOO'}

    def g():
        yield {'id': 1, 'name': 'foo'}
        yield {'id': 2, 'name': 'bar'}

    graph = Graph(g, uppercase_name)
    context = strategy.execute(graph)
    output = context.get_buffer()

    assert len(output) == 2
    assert output[0] == {'id': 1, 'name': 'FOO'}
    assert output[1] == {'id': 2, 'name': 'BAR'}

def test_node_tuple():
    def f():
        return 'foo', 'bar'

    with BufferingNodeExecutionContext(f) as context:
        context.write_sync(Bag())
        output = context.get_buffer()

        assert len(output) == 1
        assert output[0] == ('foo', 'bar')

    def g():
        yield 'foo', 'bar'
        yield 'foo', 'baz'

    with BufferingNodeExecutionContext(g) as context:
        context.write_sync(Bag())
        output = context.get_buffer()

        assert len(output) == 2
        assert output[0] == ('foo', 'bar')
        assert output[1] == ('foo', 'baz')
