from bonobo.constants import BEGIN, END
from bonobo.execution.strategies.base import Strategy
from bonobo.structs.bags import Bag


class NaiveStrategy(Strategy):
    # TODO: how to run plugins in "naive" mode ?

    def execute(self, graph, **kwargs):
        context = self.create_graph_execution_context(graph, **kwargs)
        context.write(BEGIN, Bag(), END)

        # start
        context.start()

        # loop
        nodes = list(context.nodes)
        while len(nodes):
            for node in nodes:
                node.loop()
            nodes = list(node for node in nodes if node.alive)

        # stop
        context.stop()

        return context
