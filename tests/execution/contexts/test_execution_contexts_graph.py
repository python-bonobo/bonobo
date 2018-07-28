from bonobo import Graph
from bonobo.constants import EMPTY, BEGIN, END
from bonobo.execution.contexts import GraphExecutionContext


def raise_an_error(*args, **kwargs):
    raise Exception('Careful, man, there\'s a beverage here!')


def raise_an_unrecoverrable_error(*args, **kwargs):
    raise Exception('You are entering a world of pain!')


def test_lifecycle_of_empty_graph():
    graph = Graph()
    with GraphExecutionContext(graph) as context:
        assert context.started
        assert context.alive
        assert not context.stopped
    assert context.started
    assert not context.alive
    assert context.stopped
    assert not context.xstatus


def test_lifecycle_of_nonempty_graph():
    graph = Graph([1, 2, 3], print)
    with GraphExecutionContext(graph) as context:
        assert context.started
        assert context.alive
        assert not context.stopped
    assert context.started
    assert not context.alive
    assert context.stopped
    assert not context.xstatus


def test_lifecycle_of_graph_with_recoverable_error():
    graph = Graph([1, 2, 3], raise_an_error, print)
    with GraphExecutionContext(graph) as context:
        assert context.started
        assert context.alive
        assert not context.stopped
    assert context.started
    assert not context.alive
    assert context.stopped
    assert not context.xstatus


def test_lifecycle_of_graph_with_unrecoverable_error():
    graph = Graph([1, 2, 3], raise_an_unrecoverrable_error, print)
    with GraphExecutionContext(graph) as context:
        assert context.started and context.alive and not context.stopped
        context.write(BEGIN, EMPTY, END)
        context.loop()
    assert context.started
    assert not context.alive
    assert context.stopped
    assert not context.xstatus
