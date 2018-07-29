from bonobo.execution.strategies.base import Strategy


class NaiveStrategy(Strategy):
    # TODO: how to run plugins in "naive" mode ?

    def execute(self, graph, **kwargs):
        with self.create_graph_execution_context(graph, **kwargs) as context:
            context.run_until_complete()
        return context
