import traceback
from time import sleep

from bonobo.config import Container
from bonobo.config.processors import resolve_processors, ContextCurrifier
from bonobo.util.errors import print_error
from bonobo.util.iterators import ensure_tuple
from bonobo.util.objects import Wrapper


class LoopingExecutionContext(Wrapper):
    alive = True
    PERIOD = 0.25

    @property
    def state(self):
        return self._started, self._stopped

    @property
    def started(self):
        return self._started

    @property
    def stopped(self):
        return self._stopped

    def __init__(self, wrapped, parent, services=None):
        super().__init__(wrapped)
        self.parent = parent
        if services:
            if parent:
                raise RuntimeError(
                    'Having services defined both in GraphExecutionContext and child NodeExecutionContext is not supported, for now.'
                )
            self.services = Container(services) if services else Container()
        else:
            self.services = None

        self._started, self._stopped, self._stack = False, False, None

    def start(self):
        assert self.state == (False,
                              False), ('{}.start() can only be called on a new node.').format(type(self).__name__)
        self._started = True
        self._stack = ContextCurrifier(self.wrapped, *self._get_initial_context())

        try:
            self._stack.setup(self)
        except Exception as exc:  # pylint: disable=broad-except
            self.handle_error(exc, traceback.format_exc())
            raise

    def loop(self):
        """Generic loop. A bit boring. """
        while self.alive:
            self.step()
            sleep(self.PERIOD)

    def step(self):
        """Left as an exercise for the children."""
        raise NotImplementedError('Abstract.')

    def stop(self):
        assert self._started, ('{}.stop() can only be called on a previously started node.').format(type(self).__name__)
        if self._stopped:
            return

        self._stopped = True
        try:
            self._stack.teardown()
        except Exception as exc:  # pylint: disable=broad-except
            self.handle_error(exc, traceback.format_exc())
            raise

    def handle_error(self, exc, trace):
        return print_error(exc, trace, context=self.wrapped)

    def _get_initial_context(self):
        if self.parent:
            return self.parent.services.args_for(self.wrapped)
        if self.services:
            return self.services.args_for(self.wrapped)
        return ()
