from queue import Queue, Empty

from bonobo.core.strategies.base import Strategy
from bonobo.util.iterators import force_iterator


class NaiveStrategy(Strategy):
    def execute(self, graph, *args, **kwargs):
        context = self.create_context(graph)

        input_queues = {i: Queue() for i in range(len(context.graph.components))}
        for i, component in enumerate(context.graph.components):
            while True:
                try:
                    args = (input_queues[i].get(block=False),) if i else ()
                    for row in force_iterator(component(*args)):
                        input_queues[i + 1].put(row)
                    if not i:
                        raise Empty
                except Empty:
                    break
