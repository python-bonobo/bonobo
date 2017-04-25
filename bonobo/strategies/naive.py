from bonobo.constants import BEGIN, END
from bonobo.strategies.base import Strategy
from bonobo.structs.bags import Bag


class NaiveStrategy(Strategy):
    def execute(self, graph, *args, plugins=None, **kwargs):
        context = self.create_graph_execution_context(graph, plugins=plugins)
        context.recv(BEGIN, Bag(), END)

        # TODO: how to run plugins in "naive" mode ?
        context.start()
        context.loop()
        context.stop()

        return context
