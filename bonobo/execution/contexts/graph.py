import logging
from functools import partial
from queue import Empty
from time import sleep

from whistle import EventDispatcher

from bonobo.config import create_container
from bonobo.constants import BEGIN, EMPTY, END, ERROR
from bonobo.errors import InactiveReadableError
from bonobo.execution import events
from bonobo.execution.contexts.base import BaseContext
from bonobo.execution.contexts.node import NodeExecutionContext
from bonobo.execution.contexts.plugin import PluginExecutionContext
from bonobo.structs.inputs import Pipe

logger = logging.getLogger(__name__)


class BaseGraphExecutionContext(BaseContext):
    """
    Stores the actual state of a graph execution, and manages its lifecycle. This is an abstract base class for all
    graph execution contexts, and a few methods should actually be implemented for the child classes to be useable.

    """

    NodeExecutionContextType = NodeExecutionContext
    PluginExecutionContextType = PluginExecutionContext

    TICK_PERIOD = 0.25

    @property
    def started(self):
        if not len(self.nodes):
            return super(BaseGraphExecutionContext, self).started
        return any(node.started for node in self.nodes if not node.daemon)

    @property
    def stopped(self):
        if not len(self.nodes):
            return super(BaseGraphExecutionContext, self).stopped
        return all(node.started and node.stopped for node in self.nodes if not node.daemon)

    @property
    def alive(self):
        if not len(self.nodes):
            return super(BaseGraphExecutionContext, self).alive
        return any(node.alive for node in self.nodes if not node.daemon)

    @property
    def xstatus(self):
        """
        UNIX-like exit status, only coherent if the context has stopped.

        """
        return max(node.xstatus for node in self.nodes) if len(self.nodes) else 0

    def __init__(self, graph, *, plugins=None, services=None, dispatcher=None):
        super(BaseGraphExecutionContext, self).__init__(graph)
        self.dispatcher = dispatcher or EventDispatcher()
        self.graph = graph
        self.errors = Pipe()
        errors = self.graph.outputs_of(ERROR)
        self.nodes = [
            self.create_node_execution_context_for(
                node, **({"daemon": True} if i in errors else {"_errors": self.errors})
            )
            for i, node in self.graph.items()
        ]
        self.plugins = [self.create_plugin_execution_context_for(plugin) for plugin in plugins or ()]
        self.services = create_container(services)

        # Probably not a good idea to use it unless you really know what you're doing. But you can access the context.
        self.services["__graph_context"] = self

        # Plug our error handlers if there are any
        for i in self.graph.outputs_of(ERROR):
            self[i].input.daemonize()
            self.errors.targets.append(self[i].input)

        for i, node_context in enumerate(self):
            outputs = self.graph.outputs_of(i)
            if len(outputs):
                node_context.outputs = [self[j].input for j in outputs]

                # We should propagate the "daemon" property to the next nodes in line
                if node_context.daemon:
                    for j in outputs:
                        self[j].daemonize()

            # When a signal token is sent to an input, pass it to the node context outputs so it cascade through the
            # graph.
            if not node_context.daemon:
                node_context.input.on_begin.append(partial(node_context._put, BEGIN, _control=True))
                node_context.input.on_end.append(partial(node_context._put, END, _control=True))
                node_context.input.on_finalize.append(partial(node_context.stop))

    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        yield from self.nodes

    @classmethod
    def create_queue(cls, *args, **kwargs):
        return cls.NodeExecutionContextType.create_queue(*args, **kwargs)

    def create_node_execution_context_for(self, node, **kwargs):
        return self.NodeExecutionContextType(node, parent=self, **kwargs)

    def create_plugin_execution_context_for(self, plugin):
        if isinstance(plugin, type):
            plugin = plugin()
        return self.PluginExecutionContextType(plugin, parent=self)

    def dispatch(self, name):
        self.dispatcher.dispatch(name, events.ExecutionEvent(self))

    def register_plugins(self):
        for plugin_context in self.plugins:
            plugin_context.register()

    def unregister_plugins(self):
        for plugin_context in self.plugins:
            plugin_context.unregister()


class GraphExecutionContext(BaseGraphExecutionContext):
    def start(self, starter=None):
        super(GraphExecutionContext, self).start()

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

    def stop(self, stopper=None):
        super(GraphExecutionContext, self).stop()

        self.dispatch(events.STOP)
        for node_context in self.nodes:
            if stopper is None:
                node_context.stop()
            else:
                stopper(node_context)
        self.tick(pause=False)

        self.dispatch(events.STOPPED)
        self.unregister_plugins()

    def kill(self):
        super(GraphExecutionContext, self).kill()

        self.dispatch(events.KILL)
        for node_context in self.nodes:
            node_context.kill()
        self.tick()

    def write(self, *messages):
        """Push a list of messages in the inputs of this graph's inputs, matching the output of special node "BEGIN" in
        our graph."""

        for message in messages:
            for i in self.graph.outputs_of(BEGIN):
                self[i].write(message)

    def loop(self):
        nodes = set(node for node in self.nodes if node.should_loop)
        while self.should_loop and len(nodes):
            self.tick(pause=False)
            for node in list(nodes):
                try:
                    node.step()
                except Empty:
                    continue
                except InactiveReadableError:
                    logger.debug("Discarding node {!r}.".format(node))
                    nodes.discard(node)

    def run_until_complete(self):
        self.write(BEGIN, EMPTY, END)
        self.loop()
