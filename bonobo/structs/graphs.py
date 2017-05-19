from bonobo.constants import BEGIN


class Graph:
    """
    Represents a directed graph of nodes.
    """

    def __init__(self, *chain):
        self.edges = {BEGIN: set()}
        self.named = {}
        self.nodes = []
        self.add_chain(*chain)

    def __iter__(self):
        yield from self.nodes

    def __len__(self):
        """ Node count.
        """
        return len(self.nodes)

    def __getitem__(self, key):
        return self.nodes[key]

    def outputs_of(self, idx, create=False):
        """ Get a set of the outputs for a given node index.
        """
        if create and not idx in self.edges:
            self.edges[idx] = set()
        return self.edges[idx]

    def add_node(self, c):
        """ Add a node without connections in this graph and returns its index.
        """
        idx = len(self.nodes)
        self.edges[idx] = set()
        self.nodes.append(c)
        return idx

    def add_chain(self, *nodes, _input=BEGIN, _output=None, _name=None):
        """ Add a chain in this graph.
        """
        if len(nodes):
            _input = self._resolve_index(_input)
            _output = self._resolve_index(_output)

            for i, node in enumerate(nodes):
                _next = self.add_node(node)
                if not i and _name:
                    if _name in self.named:
                        raise KeyError('Duplicate name {!r} in graph.'.format(_name))
                    self.named[_name] = _next
                self.outputs_of(_input, create=True).add(_next)
                _input = _next

            if _output is not None:
                self.outputs_of(_input, create=True).add(_output)

            if hasattr(self, '_topologcally_sorted_indexes_cache'):
                del self._topologcally_sorted_indexes_cache

        return self

    @property
    def topologically_sorted_indexes(self):
        """Iterate in topological order, based on networkx's topological_sort() function.
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

    def _resolve_index(self, mixed):
        """ Find the index based on various strategies for a node, probably an input or output of chain. Supported inputs are indexes, node values or names.
        """
        if mixed is None:
            return None

        if type(mixed) is int or mixed in self.edges:
            return mixed

        if isinstance(mixed, str) and mixed in self.named:
            return self.named[mixed]

        if mixed in self.nodes:
            return self.nodes.index(mixed)

        raise ValueError('Cannot find node matching {!r}.'.format(mixed))
