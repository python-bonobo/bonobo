import traceback
from contextlib import contextmanager
from time import sleep

from bonobo.config import Container
from bonobo.config.processors import ContextCurrifier
from bonobo.plugins import get_enhancers
from bonobo.util.errors import print_error
from bonobo.util.objects import Wrapper, get_name


@contextmanager
def recoverable(error_handler):
    try:
        yield
    except Exception as exc:  # pylint: disable=broad-except
        error_handler(exc, traceback.format_exc())


@contextmanager
def unrecoverable(error_handler):
    try:
        yield
    except Exception as exc:  # pylint: disable=broad-except
        error_handler(exc, traceback.format_exc())
        raise  # raise unrecoverableerror from x ?


class LoopingExecutionContext(Wrapper):
    alive = True
    PERIOD = 0.25

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

        self._started, self._stopped = False, False
        self._stack = None

        # XXX enhancers
        self._enhancers = get_enhancers(self.wrapped)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.stop()

    def start(self):
        if self.started:
            raise RuntimeError('Cannot start a node twice ({}).'.format(get_name(self)))

        self._started = True

        self._stack = ContextCurrifier(self.wrapped, *self._get_initial_context())
        self._stack.setup(self)

        for enhancer in self._enhancers:
            with unrecoverable(self.handle_error):
                enhancer.start(self)

    def loop(self):
        """Generic loop. A bit boring. """
        while self.alive:
            self.step()
            sleep(self.PERIOD)

    def step(self):
        """Left as an exercise for the children."""
        raise NotImplementedError('Abstract.')

    def stop(self):
        if not self.started:
            raise RuntimeError('Cannot stop an unstarted node ({}).'.format(get_name(self)))

        if self._stopped:
            return

        try:
            if self._stack:
                self._stack.teardown()
        finally:
            self._stopped = True

    def handle_error(self, exc, trace):
        return print_error(exc, trace, context=self.wrapped)

    def _get_initial_context(self):
        if self.parent:
            return self.parent.services.args_for(self.wrapped)
        if self.services:
            return self.services.args_for(self.wrapped)
        return ()
