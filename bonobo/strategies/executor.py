import functools
import logging
import sys
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor, wait, FIRST_EXCEPTION
from time import sleep

from bonobo.util import get_name
from bonobo.constants import BEGIN, END
from bonobo.strategies.base import Strategy
from bonobo.structs.bags import Bag


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

        futures = []

        with self.create_executor() as executor:
            context.start(self.get_starter(executor, futures))

            while context.alive:
                try:
                    context.tick()
                except KeyboardInterrupt:
                    logging.getLogger(__name__).warning('KeyboardInterrupt received. Trying to terminate the nodes gracefully.')
                    context.kill()
                    break

            context.stop()

        return context

    def get_starter(self, executor, futures):
        def starter(node):
            @functools.wraps(node)
            def _runner():
                try:
                    with node:
                        node.loop()
                except BaseException as exc:
                    logging.getLogger(__name__).info('Got {} in {} runner.'.format(get_name(exc), node),
                                                     exc_info=sys.exc_info())

            futures.append(executor.submit(_runner))

        return starter


class ThreadPoolExecutorStrategy(ExecutorStrategy):
    executor_factory = ThreadPoolExecutor


class ProcessPoolExecutorStrategy(ExecutorStrategy):
    executor_factory = ProcessPoolExecutor
