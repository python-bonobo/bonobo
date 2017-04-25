from bonobo.execution.graph import GraphExecutionContext


class Strategy:
    """
    Base class for execution strategies.

    """
    graph_execution_context_factory = GraphExecutionContext

    def create_graph_execution_context(self, graph, *args, **kwargs):
        return self.graph_execution_context_factory(graph, *args, **kwargs)

    def execute(self, graph, *args, **kwargs):
        raise NotImplementedError
