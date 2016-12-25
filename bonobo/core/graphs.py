from bonobo.util.tokens import Begin


class Graph:
    """
    Represents a coherent directed acyclic graph (DAG) of components.
    """

    def __init__(self):
        self.components = []
        self.graph = {Begin: set()}

    def outputs_of(self, idx, create=False):
        if create and not idx in self.graph:
            self.graph[idx] = set()
        return self.graph[idx]

    def add_component(self, c):
        i = len(self.components)
        self.components.append(c)
        return i

    def add_chain(self, *components, input=Begin):
        for component in components:
            next = self.add_component(component)
            self.outputs_of(input, create=True).add(next)
            input = next
