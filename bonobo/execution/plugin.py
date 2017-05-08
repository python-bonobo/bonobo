import traceback

from bonobo.execution.base import LoopingExecutionContext


class PluginExecutionContext(LoopingExecutionContext):
    PERIOD = 0.5

    def __init__(self, wrapped, parent):
        # Instanciate plugin. This is not yet considered stable, as at some point we may need a way to configure
        # plugins, for example if it depends on an external service.
        super().__init__(wrapped(self), parent)

    def start(self):
        super().start()

        try:
            self.wrapped.initialize()
        except Exception as exc:  # pylint: disable=broad-except
            self.handle_error(exc, traceback.format_exc())

    def shutdown(self):
        try:
            self.wrapped.finalize()
        except Exception as exc:  # pylint: disable=broad-except
            self.handle_error(exc, traceback.format_exc())
        finally:
            self.alive = False

    def step(self):
        try:
            self.wrapped.run()
        except Exception as exc:  # pylint: disable=broad-except
            self.handle_error(exc, traceback.format_exc())
