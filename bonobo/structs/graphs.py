import html
import json
from collections import namedtuple
from copy import copy

from graphviz import ExecutableNotFound
from graphviz.dot import Digraph

from bonobo.constants import BEGIN
from bonobo.util import get_name
from bonobo.util.collections import coalesce

GraphRange = namedtuple("GraphRange", ["graph", "input", "output"])


class GraphCursor:
    @property
    def input(self):
        return self.first

    @property
    def output(self):
        return self.last

    @property
    def range(self):
        return self.first, self.last

    def __init__(self, graph, *, first=None, last=None):
        self.graph = graph
        self.first = coalesce(first, last)
        self.last = last

    def __rshift__(self, other):
        """ Self >> Other """

        # Allow to concatenate cursors.
        if isinstance(other, GraphCursor):
            chain = self.graph.add_chain(_input=self.last, _output=other.first)
            return GraphCursor(chain.graph, first=self.first, last=other.last)

        # If we get a partial graph, or anything with a node list, use that.
        nodes = other.nodes if hasattr(other, "nodes") else [other]

        # Sometimes, we use ellipsis to show "pseudo-code". This is ok, but can't be executed.
        if ... in nodes:
            raise NotImplementedError(
                "Expected something looking like a node, but got an Ellipsis (...). Did you forget to complete the graph?"
            )

        # If there are nodes to add, create a new cursor after the chain is added to the graph.
        if len(nodes):
            chain = self.graph.add_chain(*nodes, _input=self.last, use_existing_nodes=True)
            return GraphCursor(chain.graph, first=coalesce(self.first, chain.input), last=chain.output)

        # If we add nothing, then nothing changed.
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def __eq__(self, other):
        try:
            return self.graph == other.graph and self.first == other.first and self.last == other.last
        except AttributeError:
            return False


class PartialGraph:
    def __init__(self, *nodes):
        self.nodes = list(nodes)


class Graph:
    """
    Core structure representing a directed graph of nodes. It will be used to create data streaming queues between your
    objects during the job execution.

    This is how the data flows are defined.

    """

    name = ""

    def __init__(self, *chain):
        self.edges = {BEGIN: set()}
        self.named = {}
        self.nodes = []
        if len(chain):
            self.add_chain(*chain)

    def __iter__(self):
        yield from self.nodes

    def __len__(self):
        """
        The graph length is defined as its node count.
        
        """
        return len(self.nodes)

    def __getitem__(self, key):
        return self.nodes[key]

    def __enter__(self):
        return self.get_cursor().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def __rshift__(self, other):
        return self.get_cursor().__rshift__(other)

    def get_cursor(self, ref=BEGIN):
        """
        Create a `GraphCursor` to use the operator-based syntax to build graph, starting at `ref`.

        """
        return GraphCursor(self, last=self.index_of(ref))

    def orphan(self):
        """
        Create a `GraphCursor` attached to nothing.

        """
        return self.get_cursor(None)

    def index_of(self, mixed):
        """
        Find the index based on various strategies for a node, probably an input or output of chain. Supported
        inputs are indexes, node values or names.

        """
        if mixed is None:
            return None

        if type(mixed) is int or mixed in self.edges:
            return mixed

        if isinstance(mixed, str) and mixed in self.named:
            return self.named[mixed]

        if mixed in self.nodes:
            return self.nodes.index(mixed)

        raise ValueError("Cannot find node matching {!r}.".format(mixed))

    def indexes_of(self, *things, _type=set):
        """
        Returns the set of indexes of the things passed as arguments.

        """
        return _type(map(self.index_of, things))

    def outputs_of(self, idx_or_node, create=False):
        """
        Get a set of the outputs for a given node, node index or name.
        
        """
        idx_or_node = self.index_of(idx_or_node)

        if create and not idx_or_node in self.edges:
            self.edges[idx_or_node] = set()
        return self.edges[idx_or_node]

    def add_node(self, new_node, *, _name=None):
        """
        Add a node without connections in this graph and returns its index.
        If _name is specified, name this node (string reference for  further usage).
        
        """
        idx = len(self.nodes)
        self.edges[idx] = set()
        self.nodes.append(new_node)

        if _name:
            if _name in self.named:
                raise KeyError("Duplicate name {!r} in graph.".format(_name))
            self.named[_name] = idx

        return idx

    def get_or_add_node(self, new_node, *, _name=None):
        if new_node in self.nodes:
            if _name is not None:
                raise RuntimeError("Cannot name a node that is already present in the graph.")
            return self.index_of(new_node)
        return self.add_node(new_node, _name=_name)

    def add_chain(self, *nodes, _input=BEGIN, _output=None, _name=None, use_existing_nodes=False):
        """
        Add `nodes` as a chain in this graph.

        **Input rules**

        * By default, this chain will be connected to `BEGIN`, a.k.a the special node that kickstarts transformations.
        * If `_input` is set to `None`, then this chain won't receive any input unless you connect it manually to
          something.
        * If `_input` is something that can resolve to another node using `index_of` rules, then the chain will
          receive the output stream of referenced node.
        
        **Output rules**

        * By default, this chain won't send its output anywhere. This is, most of the time, what you want.
        * If `_output` is set to something (that can resolve to a node), then the last node in the chain will send its
          outputs to the given node. This means you can provide an object, a name, or an index.

        **Naming**

        * If a `_name` is given, the first node in the chain will be named this way (same effect as providing a `_name`
          to add_node).

        **Special cases**

        * You can use this method to connect two other chains (in fact, two nodes) by not giving any `nodes`, but
          still providing values to `_input` and `_output`.

        """
        _input = self.index_of(_input)
        _output = self.index_of(_output)
        _first = None
        _last = None

        get_node = self.get_or_add_node if use_existing_nodes else self.add_node

        # Sanity checks.
        if not len(nodes):
            if _input is None or _output is None:
                raise ValueError(
                    "Using add_chain(...) without nodes is only possible if you provide both _input and _output values."
                )

            if _name is not None:
                raise RuntimeError("Using add_chain(...) without nodes does not allow to use the _name parameter.")

        for i, node in enumerate(nodes):
            _last = get_node(node, _name=_name if not i else None)

            if _first is None:
                _first = _last

            self.outputs_of(_input, create=True).add(_last)

            _input = _last

        if _output is not None:
            self.outputs_of(_input, create=True).add(_output)

        if hasattr(self, "_topologcally_sorted_indexes_cache"):
            del self._topologcally_sorted_indexes_cache

        return GraphRange(self, _first, _last)

    def copy(self):
        g = Graph()

        g.edges = copy(self.edges)
        g.named = copy(self.named)
        g.nodes = copy(self.nodes)

        return g

    @property
    def topologically_sorted_indexes(self):
        """
        Iterate in topological order, based on networkx's topological_sort() function.
        
        """
        try:
            return self._topologcally_sorted_indexes_cache
        except AttributeError:
            seen = set()
            order = []
            explored = set()

            for i in self.edges:
                if i in explored:
                    continue
                fringe = [i]
                while fringe:
                    w = fringe[-1]  # depth first search
                    if w in explored:  # already looked down this branch
                        fringe.pop()
                        continue
                    seen.add(w)  # mark as seen
                    # Check successors for cycles and for new nodes
                    new_nodes = []
                    for n in self.outputs_of(w):
                        if n not in explored:
                            if n in seen:  # CYCLE !!
                                raise RuntimeError("Graph contains a cycle.")
                            new_nodes.append(n)
                    if new_nodes:  # Add new_nodes to fringe
                        fringe.extend(new_nodes)
                    else:  # No new nodes so w is fully explored
                        explored.add(w)
                        order.append(w)
                        fringe.pop()  # done considering this node
            self._topologcally_sorted_indexes_cache = tuple(filter(lambda i: type(i) is int, reversed(order)))
            return self._topologcally_sorted_indexes_cache

    @property
    def graphviz(self):
        try:
            return self._graphviz
        except AttributeError:
            g = Digraph()
            g.attr(rankdir="LR")
            g.node("BEGIN", shape="point")
            for i in self.outputs_of(BEGIN):
                g.edge("BEGIN", str(i))
            for ix in self.topologically_sorted_indexes:
                g.node(str(ix), label=get_name(self[ix]))
                for iy in self.outputs_of(ix):
                    g.edge(str(ix), str(iy))
            self._graphviz = g
            return self._graphviz

    def _repr_dot_(self):
        return str(self.graphviz)

    def _repr_html_(self):
        try:
            return "<div>{}</div><pre>{}</pre>".format(self.graphviz._repr_svg_(), html.escape(repr(self)))
        except (ExecutableNotFound, FileNotFoundError) as exc:
            return "<strong>{}</strong>: {}".format(type(exc).__name__, str(exc))


def _get_graphviz_node_id(graph, i):
    escaped_index = str(i)
    escaped_name = json.dumps(get_name(graph[i]))
    return "{{{} [label={}]}}".format(escaped_index, escaped_name)
