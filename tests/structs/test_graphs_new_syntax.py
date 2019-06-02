from operator import attrgetter

import pytest

from bonobo.constants import BEGIN
from bonobo.structs.graphs import Graph, GraphCursor
from bonobo.util.testing import get_pseudo_nodes


def test_get_cursor():
    g = Graph()
    cursor = g.get_cursor()

    assert cursor.graph is g
    assert cursor.first is BEGIN
    assert cursor.last is BEGIN


def test_get_cursor_in_a_vacuum():
    g = Graph()
    cursor = g.get_cursor(None)

    assert cursor.graph is g
    assert cursor.first is None
    assert cursor.last is None


def test_cursor_usage_to_add_a_chain():
    a, b, c = get_pseudo_nodes(*"abc")

    g = Graph()

    g.get_cursor() >> a >> b >> c

    assert len(g) == 3
    assert g.outputs_of(BEGIN) == {g.index_of(a)}
    assert g.outputs_of(a) == {g.index_of(b)}
    assert g.outputs_of(b) == {g.index_of(c)}
    assert g.outputs_of(c) == set()


def test_cursor_usage_to_add_a_chain_in_a_context_manager():
    a, b, c = get_pseudo_nodes(*"abc")

    g = Graph()
    with g as cur:
        cur >> a >> b >> c

    assert len(g) == 3
    assert g.outputs_of(BEGIN) == {g.index_of(a)}
    assert g.outputs_of(a) == {g.index_of(b)}
    assert g.outputs_of(b) == {g.index_of(c)}
    assert g.outputs_of(c) == set()


def test_implicit_cursor_usage():
    a, b, c = get_pseudo_nodes(*"abc")

    g = Graph()
    g >> a >> b >> c

    assert len(g) == 3
    assert g.outputs_of(BEGIN) == {g.index_of(a)}
    assert g.outputs_of(a) == {g.index_of(b)}
    assert g.outputs_of(b) == {g.index_of(c)}
    assert g.outputs_of(c) == set()


def test_cursor_to_fork_a_graph():
    a, b, c, d, e = get_pseudo_nodes(*"abcde")

    g = Graph()
    g >> a >> b >> c
    g.get_cursor(b) >> d >> e

    assert len(g) == 5
    assert g.outputs_of(BEGIN) == {g.index_of(a)}
    assert g.outputs_of(a) == {g.index_of(b)}
    assert g.outputs_of(b) == {g.index_of(c), g.index_of(d)}
    assert g.outputs_of(c) == set()
    assert g.outputs_of(d) == {g.index_of(e)}
    assert g.outputs_of(e) == set()


def test_cursor_to_fork_at_the_end():
    a, b, c, d, e = get_pseudo_nodes(*"abcde")

    g = Graph()
    c0 = g >> a >> b
    c1 = c0 >> c
    c2 = c0 >> d >> e

    assert len(g) == 5
    assert g.outputs_of(BEGIN) == {g.index_of(a)}
    assert g.outputs_of(a) == {g.index_of(b)}
    assert g.outputs_of(b) == {g.index_of(c), g.index_of(d)}
    assert g.outputs_of(c) == set()
    assert g.outputs_of(d) == {g.index_of(e)}
    assert g.outputs_of(e) == set()

    assert c0.first == g.index_of(BEGIN)
    assert c0.last == g.index_of(b)
    assert c1.first == g.index_of(BEGIN)
    assert c1.last == g.index_of(c)
    assert c2.first == g.index_of(BEGIN)
    assert c2.last == g.index_of(e)


def test_cursor_merge():
    a, b, c = get_pseudo_nodes(*"abc")
    g = Graph()

    c1 = g >> a >> c
    c2 = g >> b >> c

    assert len(g) == 3
    assert g.outputs_of(BEGIN) == g.indexes_of(a, b)
    assert g.outputs_of(a) == g.indexes_of(c)
    assert g.outputs_of(b) == g.indexes_of(c)
    assert g.outputs_of(c) == set()

    assert c1 == c2


def test_cursor_merge_orphan_in_between():
    a, b, c, v, w, x, y = get_pseudo_nodes(*"abcdefg")
    g = Graph()
    g >> a >> b >> c
    assert len(g) == 3
    g.orphan() >> v >> w >> b
    assert len(g) == 5
    g.orphan() >> x >> y >> b
    assert len(g) == 7

    assert g.outputs_of(BEGIN) == g.indexes_of(a)
    assert g.outputs_of(a) == g.indexes_of(b)
    assert g.outputs_of(b) == g.indexes_of(c)
    assert g.outputs_of(c) == set()
    assert g.outputs_of(v) == g.indexes_of(w)
    assert g.outputs_of(w) == g.indexes_of(b)
    assert g.outputs_of(x) == g.indexes_of(y)
    assert g.outputs_of(y) == g.indexes_of(b)


def test_using_same_cursor_many_times_for_fork():
    a, b, c, d, e = get_pseudo_nodes(5)
    g = Graph()

    c0 = g >> a >> b

    c0 >> c
    c0 >> d
    c0 >> e

    assert g.outputs_of(BEGIN) == g.indexes_of(a)
    assert g.outputs_of(a) == g.indexes_of(b)
    assert g.outputs_of(b) == g.indexes_of(c, d, e)
    assert g.outputs_of(c) == set()
    assert g.outputs_of(d) == set()
    assert g.outputs_of(e) == set()


def test_concat_branches():
    a, b, c, d = get_pseudo_nodes(4)
    g = Graph()

    c0 = g.orphan() >> a >> b
    c1 = g >> c >> d
    c2 = c1 >> c0

    assert c2.first == BEGIN
    assert c2.last == g.index_of(b)
