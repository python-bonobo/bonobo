from bonobo.execution.contexts.graph import GraphExecutionContext


class Strategy:
    """
    Base class for execution strategies.

    """

    GraphExecutionContextType = GraphExecutionContext

    def __init__(self, GraphExecutionContextType=None):
        self.GraphExecutionContextType = GraphExecutionContextType or self.GraphExecutionContextType

    def create_graph_execution_context(self, graph, *args, GraphExecutionContextType=None, **kwargs):
        if not len(graph):
            raise ValueError("You provided an empty graph, which does not really make sense. Please add some nodes.")
        return (GraphExecutionContextType or self.GraphExecutionContextType)(graph, *args, **kwargs)

    def execute(self, graph, *args, **kwargs):
        raise NotImplementedError
