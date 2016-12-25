from bonobo.core.strategies.base import Strategy


class NaiveStrategy(Strategy):
    def execute(self, graph, *args, plugins=None, **kwargs):
        context = self.create_context(graph, plugins=plugins)
        context.impulse()

        # TODO: how to run plugins in "naive" mode ?

        for component in context.components:
            component.run()

        return context
