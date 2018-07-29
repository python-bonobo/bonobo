from bonobo.config.processors import use_context_processor
from bonobo.constants import BEGIN, END
from bonobo.execution.contexts.graph import GraphExecutionContext
from bonobo.execution.strategies import NaiveStrategy
from bonobo.structs.graphs import Graph


def generate_integers():
    yield from range(10)


def square(i):
    return i**2


def results(f, context):
    results = yield list()
    context.parent.results = results


@use_context_processor(results)
def push_result(results, i):
    results.append(i)


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

    context.write(BEGIN, (), END)

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
