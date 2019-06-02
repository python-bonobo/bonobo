from unittest.mock import sentinel

import pytest

from bonobo.constants import BEGIN
from bonobo.structs.graphs import Graph
from bonobo.util.testing import get_pseudo_nodes

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


def test_graph_index_of():
    g = Graph()

    foo, bar, not_there = get_pseudo_nodes("foo", "bar", "not_there")

    g.add_node(foo)
    g.add_node(bar)

    # sequential, can resolve objects
    assert g.index_of(foo) == 0
    assert g.index_of(bar) == 1

    # calling on an index should return the index
    assert g.index_of(bar) == g.index_of(g.index_of(bar))

    # not existing should raise value error
    with pytest.raises(ValueError):
        g.index_of(not_there)

    # tokens resolve to themselves
    assert g.index_of(BEGIN) == BEGIN


def test_graph_add_component():
    g = Graph()

    assert len(g.nodes) == 0

    g.add_node(identity)
    assert len(g.nodes) == 1

    g.add_node(identity)
    assert len(g.nodes) == 2


def test_invalid_graph_usage():
    g = Graph()
    foo, bar = get_pseudo_nodes("foo", "bar")

    with pytest.raises(ValueError):
        g.add_chain()

    g.add_node(foo)
    g.add_node(bar)

    with pytest.raises(RuntimeError):
        g.add_chain(_input=bar, _output=foo, _name="this_is_not_possible")


def test_graph_add_chain():
    g = Graph()

    assert len(g.nodes) == 0

    g.add_chain(identity, identity, identity)
    assert len(g.nodes) == 3
    assert len(g.outputs_of(BEGIN)) == 1


def test_graph_topological_sort():
    g = Graph()
    a1, a2, a3, b1, b2 = get_pseudo_nodes("a1", "a2", "a3", "b1", "b2")

    g.add_chain(a1, a2, a3, _input=None, _output=None)

    assert g.topologically_sorted_indexes == (0, 1, 2)
    assert g[0] == a1
    assert g[1] == a2
    assert g[2] == a3

    g.add_chain(b1, b2, _output=a2)

    assert g.topologically_sorted_indexes[-2:] == (1, 2)
    assert g.topologically_sorted_indexes.index(3) < g.topologically_sorted_indexes.index(4)
    assert g[3] == b1
    assert g[4] == b2


def test_connect_two_chains():
    g = Graph()
    a1, a2, b1, b2 = get_pseudo_nodes("a1", "a2", "b1", "b2")

    g.add_chain(a1, a2, _input=None, _output=None)
    g.add_chain(b1, b2, _input=None, _output=None)
    assert len(g.outputs_of(a2)) == 0

    g.add_chain(_input=a2, _output=b1)
    assert g.outputs_of(a2) == g.indexes_of(b1)


def test_connect_two_anonymous_nodes():
    g = Graph()
    a, b = get_pseudo_nodes(*"ab")

    # Create two "anonymous" nodes
    g.add_node(a)
    g.add_node(b)

    # Connect them
    g.add_chain(_input=a, _output=b)


def test_named_nodes():
    g = Graph()

    a, b, c, d, e, f = get_pseudo_nodes(*"abcdef")

    # Here we mark _input to None, so normalize won't get the "begin" impulsion.
    g.add_chain(e, f, _input=None, _name="load")

    # Add two different chains
    g.add_chain(a, b, _output="load")
    g.add_chain(c, d, _output="load")


def test_copy():
    g1 = Graph()
    g2 = g1.copy()

    assert g1 is not g2

    assert len(g1) == 0
    assert len(g2) == 0

    g1.add_chain([])

    assert len(g1) == 1
    assert len(g2) == 0

    g2.add_chain([], identity)

    assert len(g1) == 1
    assert len(g2) == 2
