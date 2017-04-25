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
        self.nodes = [NodeExecutionContext(node, parent=self) for node in self.graph.nodes]
        self.plugins = [PluginExecutionContext(plugin, parent=self) for plugin in plugins or ()]
        self.services = Container(services) if services else Container()

        for i, component_context in enumerate(self):
            try:
                component_context.outputs = [self[j].input for j in self.graph.outputs_of(i)]
            except KeyError:
                continue

            component_context.input.on_begin = partial(component_context.send, BEGIN, _control=True)
            component_context.input.on_end = partial(component_context.send, END, _control=True)
            component_context.input.on_finalize = partial(component_context.stop)

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
                self[i].recv(message)

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
