from whistle import EventDispatcher

from bonobo.execution.reloaded.nodes import Node


class Job:
    def __init__(self, graph, *, dispatcher=None):
        self.dispatcher = dispatcher or EventDispatcher()
        self.graph = graph
        self.nodes = [Node(handler) for handler in self.graph]
