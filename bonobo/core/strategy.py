import time
from concurrent.futures import Executor
from queue import Queue, Empty

from bonobo.core.io import Input
from bonobo.core.tokens import BEGIN
from bonobo.util.iterators import force_iterator


class Strategy:
    def execute(self, graph, *args, **kwargs):
        raise NotImplementedError


class NaiveStrategy(Strategy):
    def execute(self, graph, *args, **kwargs):
        input_queues = {i: Queue() for i in range(len(graph.components))}
        for i, component in enumerate(graph.components):
            while True:
                try:
                    args = (input_queues[i].get(block=False),) if i else ()
                    for row in force_iterator(component(*args)):
                        input_queues[i + 1].put(row)
                    if not i:
                        raise Empty
                except Empty:
                    break


class ExecutionContext:
    def __init__(self, graph):
        self.graph = graph


class ExecutorStrategy(Strategy):
    context_type = ExecutionContext
    executor_type = Executor

    def __init__(self, executor=None):
        self.executor = executor or self.executor_type()

    def create_context(self, graph, *args, **kwargs):
        return self.context_type(graph)

    def execute(self, graph, *args, **kwargs):
        context = self.create_context(graph)

        for i in graph.outputs_of(BEGIN):
            self.call_component(i, *args, **kwargs)

        while len(self.running):
            # print(self.running)
            time.sleep(0.1)

        f = self.executor.submit(self.components[idx], *args, **kwargs)
        self.running.add(f)

        @f.add_done_callback
        def on_component_done(f):
            nonlocal self, idx

            outputs = self.outputs_of(idx)
            results = force_iterator(f.result())

            if results:
                for result in results:
                    for output in outputs:
                        self.call_component(output, result)

            self.running.remove(f)

    def __run_component(self, component):
        c_in = Input()

        while c_in.alive:
            row = c_in.get()
            component(row)
