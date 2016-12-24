from bonobo.core.contexts import ExecutionContext


class Strategy:
    """
    Base class for execution strategies.

    """
    context_type = ExecutionContext

    def create_context(self, graph, *args, **kwargs):
        return self.context_type(graph, *args, **kwargs)

    def execute(self, graph, *args, **kwargs):
        raise NotImplementedError
