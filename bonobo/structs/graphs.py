from bonobo.constants import BEGIN


class Graph:
    """
    Represents a coherent directed acyclic graph of components.
    """

    def __init__(self, *chain):
        self.nodes = []
        self.graph = {BEGIN: set()}
        self.add_chain(*chain)

    def outputs_of(self, idx, create=False):
        if create and not idx in self.graph:
            self.graph[idx] = set()
        return self.graph[idx]

    def add_node(self, c):
        i = len(self.nodes)
        self.nodes.append(c)
        return i

    def add_chain(self, *nodes, _input=BEGIN, _output=None):
        for node in nodes:
            _next = self.add_node(node)
            self.outputs_of(_input, create=True).add(_next)
            _input = _next
        if _output:
            if not _output in self.nodes:
                raise ValueError('Output not found.')
            self.outputs_of(_input, create=True).add(self.nodes.index(_output))

        return self

    def __len__(self):
        return len(self.nodes)
