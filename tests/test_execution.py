from bonobo.config.processors import ContextProcessor
from bonobo.constants import BEGIN, END
from bonobo.execution.graph import GraphExecutionContext
from bonobo.strategies import NaiveStrategy
from bonobo.structs import Bag, Graph


def generate_integers():
    yield from range(10)


def square(i: int) -> int:
    return i**2


def push_result(results, i: int):
    results.append(i)


@ContextProcessor.decorate(push_result)
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

    context = GraphExecutionContext(graph)
    assert len(context.nodes) == len(chain)
    assert not len(context.plugins)

    for i, node in enumerate(chain):
        assert context[i].wrapped is node

    assert not context.alive
    assert not context.started
    assert not context.stopped

    context.write(BEGIN, Bag(), END)

    assert not context.alive
    assert not context.started
    assert not context.stopped

    context.start()

    assert context.alive
    assert context.started
    assert not context.stopped

    context.stop()

    assert not context.alive
    assert context.started
    assert context.stopped
