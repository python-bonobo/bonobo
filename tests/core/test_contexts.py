from bonobo import Graph, NaiveStrategy, Bag
from bonobo.core.contexts import ExecutionContext
from bonobo.util.lifecycle import with_context
from bonobo.util.tokens import BEGIN, END


def generate_integers():
    yield from range(10)


def square(i: int) -> int:
    return i**2


@with_context
def push_result(ctx, i: int):
    if not hasattr(ctx.parent, 'results'):
        ctx.parent.results = []
    ctx.parent.results.append(i)


chain = (generate_integers, square, push_result)


def test_empty_execution_context():
    graph = Graph()

    ctx = ExecutionContext(graph)
    assert not len(ctx.components)
    assert not len(ctx.plugins)

    assert not ctx.alive


def test_execution():
    graph = Graph()
    graph.add_chain(*chain)

    strategy = NaiveStrategy()
    ctx = strategy.execute(graph)

    assert ctx.results == [1, 4, 9, 16, 25, 36, 49, 64, 81]


def test_simple_execution_context():
    graph = Graph()
    graph.add_chain(*chain)

    ctx = ExecutionContext(graph)
    assert len(ctx.components) == len(chain)
    assert not len(ctx.plugins)

    for i, component in enumerate(chain):
        assert ctx[i].component is component

    assert not ctx.alive

    ctx.recv(BEGIN, Bag(), END)

    assert ctx.alive
