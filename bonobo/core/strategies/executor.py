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

    def execute(self, graph, *args, plugins=None, **kwargs):
        context = self.create_context(graph, plugins=plugins)
        context.recv(BEGIN, Bag(), END)

        executor = self.executor_factory()

        futures = []

        for plugin_context in context.plugins:
            futures.append(executor.submit(plugin_context.run))

        for component_context in context.components:
            futures.append(executor.submit(component_context.run))

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
        context = self.create_context(graph, plugins=plugins)
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
