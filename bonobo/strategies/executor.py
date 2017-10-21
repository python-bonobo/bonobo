import time
import traceback
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor

from bonobo.constants import BEGIN, END
from bonobo.strategies.base import Strategy
from bonobo.structs.bags import Bag
from bonobo.util.errors import print_error


class ExecutorStrategy(Strategy):
    """
    Strategy based on a concurrent.futures.Executor subclass (or similar interface).

    """

    executor_factory = Executor

    def create_executor(self):
        return self.executor_factory()

    def execute(self, graph, **kwargs):
        context = self.create_graph_execution_context(graph, **kwargs)
        context.write(BEGIN, Bag(), END)

        executor = self.create_executor()

        futures = []

        context.start_plugins(self.get_plugin_starter(executor, futures))
        context.start(self.get_starter(executor, futures))

        while context.alive:
            time.sleep(0.1)

        for plugin_context in context.plugins:
            plugin_context.shutdown()

        context.stop()

        executor.shutdown()

        return context

    def get_starter(self, executor, futures):
        def starter(node):
            def _runner():
                try:
                    node.start()
                except Exception as exc:
                    print_error(exc, traceback.format_exc(), context=node, method='start')
                    node.input.on_end()
                else:
                    node.loop()

                try:
                    node.stop()
                except Exception as exc:
                    print_error(exc, traceback.format_exc(), context=node, method='stop')

            futures.append(executor.submit(_runner))

        return starter

    def get_plugin_starter(self, executor, futures):
        def plugin_starter(plugin):
            def _runner():
                with plugin:
                    try:
                        plugin.loop()
                    except Exception as exc:
                        print_error(exc, traceback.format_exc(), context=plugin)

            futures.append(executor.submit(_runner))

        return plugin_starter


class ThreadPoolExecutorStrategy(ExecutorStrategy):
    executor_factory = ThreadPoolExecutor


class ProcessPoolExecutorStrategy(ExecutorStrategy):
    executor_factory = ProcessPoolExecutor
