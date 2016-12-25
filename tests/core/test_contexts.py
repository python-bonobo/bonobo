from bonobo import Graph
from bonobo.core.contexts import ExecutionContext


def generate_integers():
    yield from range(10)


def square(i: int) -> int:
    return i**2


def test_empty_execution_context():
    graph = Graph()

    ctx = ExecutionContext(graph)
    assert not len(ctx.components)
    assert not len(ctx.plugins)

    assert not ctx.running


def test_simple_execution_context():
    graph = Graph()
    graph.add_chain(generate_integers, square)

    ctx = ExecutionContext(graph)
    assert len(ctx.components) == 2
    assert not len(ctx.plugins)

    assert ctx[0].component is generate_integers
    assert ctx[1].component is square

    assert not ctx.running
