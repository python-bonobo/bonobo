import time
import traceback
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor

from bonobo.constants import BEGIN, END
from bonobo.strategies.base import Strategy
from bonobo.structs.bags import Bag
from bonobo.util.errors import print_error


def _plugin_runner(plugin_context):
    with plugin_context:
        try:
            plugin_context.loop()
        except Exception as exc:
            print_error(exc, traceback.format_exc(), context=plugin_context)


def _node_runner(node_context):
    try:
        node_context.start()
    except Exception as exc:
        print_error(exc, traceback.format_exc(), context=node_context, method='start')
        node_context.input.on_end()
    else:
        node_context.loop()

    try:
        node_context.stop()
    except Exception as exc:
        print_error(exc, traceback.format_exc(), context=node_context, method='stop')



class ExecutorStrategy(Strategy):
    """
    Strategy based on a concurrent.futures.Executor subclass (or similar interface).

    """

    executor_factory = Executor

    def create_executor(self):
        return self.executor_factory()

    def execute(self, graph, *args, plugins=None, services=None, **kwargs):
        context = self.create_graph_execution_context(graph, plugins=plugins, services=services)
        context.recv(BEGIN, Bag(), END)

        executor = self.create_executor()

        futures = []

        for plugin_context in context.plugins:
            futures.append(executor.submit(_plugin_runner))

        for node_context in context.nodes:
            futures.append(executor.submit(_node_runner))

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
