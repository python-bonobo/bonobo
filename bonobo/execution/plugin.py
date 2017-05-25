from bonobo.execution.base import LoopingExecutionContext, recoverable


class PluginExecutionContext(LoopingExecutionContext):
    PERIOD = 0.5

    def __init__(self, wrapped, parent):
        # Instanciate plugin. This is not yet considered stable, as at some point we may need a way to configure
        # plugins, for example if it depends on an external service.
        super().__init__(wrapped(self), parent)

    def start(self):
        super().start()

        with recoverable(self.handle_error):
            self.wrapped.initialize()

    def shutdown(self):
        with recoverable(self.handle_error):
            self.wrapped.finalize()
        self.alive = False

    def step(self):
        with recoverable(self.handle_error):
            self.wrapped.run()
