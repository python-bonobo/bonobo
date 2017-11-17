from bonobo.execution.contexts.base import BaseContext


class PluginExecutionContext(BaseContext):
    @property
    def dispatcher(self):
        return self.parent.dispatcher

    def register(self):
        return self.wrapped.register(self.dispatcher)

    def unregister(self):
        return self.wrapped.unregister(self.dispatcher)
