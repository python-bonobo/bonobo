import pytest

from unittest.mock import sentinel

from bonobo.constants import BEGIN
from bonobo.structs import Graph

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

    assert len(g.nodes) == 0

    g.add_node(identity)
    assert len(g.nodes) == 1

    g.add_node(identity)
    assert len(g.nodes) == 2


def test_graph_add_chain():
    g = Graph()

    assert len(g.nodes) == 0

    g.add_chain(identity, identity, identity)
    assert len(g.nodes) == 3
    assert len(g.outputs_of(BEGIN)) == 1


def test_graph_topological_sort():
    g = Graph()

    g.add_chain(
        sentinel.a1,
        sentinel.a2,
        sentinel.a3,
        _input=None,
        _output=None,
    )

    assert g.topologically_sorted_indexes == (0, 1, 2)
    assert g[0] == sentinel.a1
    assert g[1] == sentinel.a2
    assert g[2] == sentinel.a3

    g.add_chain(
        sentinel.b1,
        sentinel.b2,
        _output=sentinel.a2,
    )

    assert g.topologically_sorted_indexes[-2:] == (1, 2)
    assert g.topologically_sorted_indexes.index(3) < g.topologically_sorted_indexes.index(4)
    assert g[3] == sentinel.b1
    assert g[4] == sentinel.b2
