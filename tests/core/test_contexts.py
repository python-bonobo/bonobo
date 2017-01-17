from bonobo import Graph, NaiveStrategy, Bag, contextual
from bonobo.context.execution import GraphExecutionContext
from bonobo.util.tokens import BEGIN, END


def generate_integers():
    yield from range(10)


def square(i: int) -> int:
    return i**2


@contextual
def push_result(results, i: int):
    results.append(i)


@push_result.__processors__.append
def results(f, context):
    results = []
    yield results
    context.parent.results = results


chain = (generate_integers, square, push_result)


def test_empty_execution_context():
    graph = Graph()

    ctx = GraphExecutionContext(graph)
    assert not len(ctx.nodes)
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

    ctx = GraphExecutionContext(graph)
    assert len(ctx.nodes) == len(chain)
    assert not len(ctx.plugins)

    for i, node in enumerate(chain):
        assert ctx[i].wrapped is node

    assert not ctx.alive

    ctx.recv(BEGIN, Bag(), END)

    assert not ctx.alive

    ctx.start()

    assert ctx.alive
