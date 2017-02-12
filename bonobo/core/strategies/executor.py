import time
from concurrent.futures import Executor
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from bonobo.core.strategies.base import Strategy
from bonobo.util.tokens import BEGIN, END
from ..bags import Bag


class ExecutorStrategy(Strategy):
    """
    Strategy based on a concurrent.futures.Executor subclass (or similar interface).

    """

    executor_factory = Executor

    def create_executor(self):
        return self.executor_factory()

    def execute(self, graph, *args, plugins=None, **kwargs):
        context = self.create_graph_execution_context(graph, plugins=plugins)

        context.recv(BEGIN, Bag(), END)

        executor = self.create_executor()

        futures = []

        for plugin_context in context.plugins:

            def _runner(plugin_context=plugin_context):
                plugin_context.start()
                plugin_context.loop()
                plugin_context.stop()

            futures.append(executor.submit(_runner))

        for node_context in context.nodes:

            def _runner(node_context=node_context):
                node_context.start()
                node_context.loop()

            futures.append(executor.submit(_runner))

        while context.alive:
            time.sleep(0.2)

        for plugin_context in context.plugins:
            plugin_context.shutdown()

        executor.shutdown()

        return context


class ThreadPoolExecutorStrategy(ExecutorStrategy):
    executor_factory = ThreadPoolExecutor


class ProcessPoolExecutorStrategy(ExecutorStrategy):
    executor_factory = ProcessPoolExecutor


class ThreadCollectionStrategy(Strategy):
    def execute(self, graph, *args, plugins=None, **kwargs):
        context = self.create_graph_execution_context(graph, plugins=plugins)
        context.recv(BEGIN, Bag(), END)

        threads = []

        # for plugin_context in context.plugins:
        #    threads.append(executor.submit(plugin_context.run))

        for component_context in context.components:
            thread = Thread(target=component_context.run)
            threads.append(thread)
            thread.start()

        # XXX TODO PLUGINS
        while context.alive and len(threads):
            time.sleep(0.1)
            threads = list(filter(lambda thread: thread.is_alive, threads))

        # for plugin_context in context.plugins:
        #    plugin_context.shutdown()

        # executor.shutdown()

        return context
