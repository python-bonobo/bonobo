from functools import partial

from bonobo.config.services import Container
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.execution.plugin import PluginExecutionContext


class GraphExecutionContext:
    @property
    def started(self):
        return any(node.started for node in self.nodes)

    @property
    def stopped(self):
        return all(node.started and node.stopped for node in self.nodes)

    @property
    def alive(self):
        return any(node.alive for node in self.nodes)

    def __init__(self, graph, plugins=None, services=None):
        self.graph = graph
        self.nodes = [NodeExecutionContext(node, parent=self) for node in self.graph]
        self.plugins = [PluginExecutionContext(plugin, parent=self) for plugin in plugins or ()]
        self.services = Container(services) if services else Container()

        for i, node_context in enumerate(self):
            node_context.outputs = [self[j].input for j in self.graph.outputs_of(i)]
            node_context.input.on_begin = partial(node_context.send, BEGIN, _control=True)
            node_context.input.on_end = partial(node_context.send, END, _control=True)
            node_context.input.on_finalize = partial(node_context.stop)

    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        yield from self.nodes

    def recv(self, *messages):
        """Push a list of messages in the inputs of this graph's inputs, matching the output of special node "BEGIN" in
        our graph."""

        for i in self.graph.outputs_of(BEGIN):
            for message in messages:
                self[i].write(message)

    def start(self):
        # todo use strategy
        for node in self.nodes:
            node.start()

    def loop(self):
        # todo use strategy
        for node in self.nodes:
            node.loop()

    def stop(self):
        # todo use strategy
        for node in self.nodes:
            node.stop()
