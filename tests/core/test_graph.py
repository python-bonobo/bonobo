import pytest

from bonobo.core.graphs import Graph
from bonobo.util.tokens import BEGIN

identity = lambda x: x


def test_graph_outputs_of():
    g = Graph()

    # default graph only node
    assert len(g.outputs_of(BEGIN)) == 0

    # unexisting node
    with pytest.raises(KeyError):
        g.outputs_of(0)

    # create node
    assert len(g.outputs_of(0, create=True)) == 0
    assert len(g.outputs_of(0)) == 0


def test_graph_add_component():
    g = Graph()

    assert len(g.components) == 0

    g.add_component(identity)
    assert len(g.components) == 1

    g.add_component(identity)
    assert len(g.components) == 2


def test_graph_add_chain():
    g = Graph()

    assert len(g.components) == 0

    g.add_chain(identity, identity, identity)
    assert len(g.components) == 3
    assert len(g.outputs_of(BEGIN)) == 1
