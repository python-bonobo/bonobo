from bonobo.util.tokens import BEGIN


class Graph:
    """
    Represents a coherent directed acyclic graph (DAG) of components.
    """

    def __init__(self, *chain):
        self.components = []
        self.graph = {BEGIN: set()}
        self.add_chain(*chain)

    def outputs_of(self, idx, create=False):
        if create and not idx in self.graph:
            self.graph[idx] = set()
        return self.graph[idx]

    def add_component(self, c):
        i = len(self.components)
        self.components.append(c)
        return i

    def add_chain(self, *components, _input=BEGIN):
        for component in components:
            _next = self.add_component(component)
            self.outputs_of(_input, create=True).add(_next)
            _input = _next
