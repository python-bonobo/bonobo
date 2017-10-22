import time
from functools import partial

from bonobo.config import create_container
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.execution.plugin import PluginExecutionContext
from whistle import EventDispatcher


class GraphExecutionContext:
    NodeExecutionContextType = NodeExecutionContext
    PluginExecutionContextType = PluginExecutionContext

    @property
    def started(self):
        return any(node.started for node in self.nodes)

    @property
    def stopped(self):
        return all(node.started and node.stopped for node in self.nodes)

    @property
    def alive(self):
        return any(node.alive for node in self.nodes)

    @property
    def dispatcher(self):
        try:
            return self._dispatcher
        except AttributeError:
            self._dispatcher = EventDispatcher()
            return self._dispatcher

    def __init__(self, graph, plugins=None, services=None):
        self.graph = graph
        self.nodes = [self.create_node_execution_context_for(node) for node in self.graph]
        self.plugins = [self.create_plugin_execution_context_for(plugin) for plugin in plugins or ()]
        self.services = create_container(services)

        # Probably not a good idea to use it unless you really know what you're doing. But you can access the context.
        self.services['__graph_context'] = self

        for i, node_context in enumerate(self):
            outputs = self.graph.outputs_of(i)
            if len(outputs):
                node_context.outputs = [self[j].input for j in outputs]
            node_context.input.on_begin = partial(node_context.send, BEGIN, _control=True)
            node_context.input.on_end = partial(node_context.send, END, _control=True)
            node_context.input.on_finalize = partial(node_context.stop)

    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        yield from self.nodes

    def create_node_execution_context_for(self, node):
        return self.NodeExecutionContextType(node, parent=self)

    def create_plugin_execution_context_for(self, plugin):
        return self.PluginExecutionContextType(plugin, parent=self)

    def write(self, *messages):
        """Push a list of messages in the inputs of this graph's inputs, matching the output of special node "BEGIN" in
        our graph."""

        for i in self.graph.outputs_of(BEGIN):
            for message in messages:
                self[i].write(message)

    def start(self, starter=None):
        for node in self.nodes:
            if starter is None:
                node.start()
            else:
                starter(node)

    def start_plugins(self, starter=None):
        for plugin in self.plugins:
            if starter is None:
                plugin.start()
            else:
                starter(plugin)

    def stop(self, stopper=None):
        for node in self.nodes:
            if stopper is None:
                node.stop()
            else:
                stopper(node)
