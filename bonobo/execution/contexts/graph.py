from functools import partial
from time import sleep

from whistle import EventDispatcher

from bonobo.config import create_container
from bonobo.constants import BEGIN, END
from bonobo.execution import events
from bonobo.execution.contexts.node import NodeExecutionContext
from bonobo.execution.contexts.plugin import PluginExecutionContext


class GraphExecutionContext:
    NodeExecutionContextType = NodeExecutionContext
    PluginExecutionContextType = PluginExecutionContext

    TICK_PERIOD = 0.25

    @property
    def started(self):
        return any(node.started for node in self.nodes)

    @property
    def stopped(self):
        return all(node.started and node.stopped for node in self.nodes)

    @property
    def alive(self):
        return any(node.alive for node in self.nodes)

    def __init__(self, graph, plugins=None, services=None, dispatcher=None):
        self.dispatcher = dispatcher or EventDispatcher()
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
            node_context.input.on_begin = partial(node_context._send, BEGIN, _control=True)
            node_context.input.on_end = partial(node_context._send, END, _control=True)
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
        if isinstance(plugin, type):
            plugin = plugin()
        return self.PluginExecutionContextType(plugin, parent=self)

    def write(self, *messages):
        """Push a list of messages in the inputs of this graph's inputs, matching the output of special node "BEGIN" in
        our graph."""

        for i in self.graph.outputs_of(BEGIN):
            for message in messages:
                self[i].write(message)

    def dispatch(self, name):
        self.dispatcher.dispatch(name, events.ExecutionEvent(self))

    def start(self, starter=None):
        self.register_plugins()
        self.dispatch(events.START)
        self.tick(pause=False)
        for node in self.nodes:
            if starter is None:
                node.start()
            else:
                starter(node)
        self.dispatch(events.STARTED)

    def tick(self, pause=True):
        self.dispatch(events.TICK)
        if pause:
            sleep(self.TICK_PERIOD)

    def kill(self):
        self.dispatch(events.KILL)
        for node_context in self.nodes:
            node_context.kill()
        self.tick()

    def stop(self, stopper=None):
        self.dispatch(events.STOP)
        for node_context in self.nodes:
            if stopper is None:
                node_context.stop()
            else:
                stopper(node_context)
        self.tick(pause=False)
        self.dispatch(events.STOPPED)
        self.unregister_plugins()

    def register_plugins(self):
        for plugin_context in self.plugins:
            plugin_context.register()

    def unregister_plugins(self):
        for plugin_context in self.plugins:
            plugin_context.unregister()
