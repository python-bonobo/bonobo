import time

from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor

from bonobo.constants import BEGIN, END
from bonobo.core.strategies.base import Strategy
from bonobo.structs.bags import Bag


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
