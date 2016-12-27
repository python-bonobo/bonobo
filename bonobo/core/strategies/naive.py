from bonobo.core.strategies.base import Strategy
from bonobo.util.tokens import BEGIN, END

from ..bags import Bag


class NaiveStrategy(Strategy):
    def execute(self, graph, *args, plugins=None, **kwargs):
        context = self.create_context(graph, plugins=plugins)
        context.recv(BEGIN, Bag(), END)

        # TODO: how to run plugins in "naive" mode ?

        for component in context.components:
            component.run()

        return context
