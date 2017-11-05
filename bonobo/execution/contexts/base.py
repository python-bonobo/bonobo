import logging
import sys
from contextlib import contextmanager
from logging import WARNING, ERROR

import mondrian
from bonobo.config import create_container
from bonobo.config.processors import ContextCurrifier
from bonobo.execution import logger
from bonobo.util import isconfigurabletype
from bonobo.util.objects import Wrapper, get_name


@contextmanager
def recoverable(error_handler):
    try:
        yield
    except Exception as exc:  # pylint: disable=broad-except
        error_handler(*sys.exc_info(), level=ERROR)


@contextmanager
def unrecoverable(error_handler):
    try:
        yield
    except Exception as exc:  # pylint: disable=broad-except
        error_handler(*sys.exc_info(), level=ERROR)
        raise  # raise unrecoverableerror from x ?


class LoopingExecutionContext(Wrapper):
    PERIOD = 0.5

    @property
    def started(self):
        return self._started

    @property
    def stopped(self):
        return self._stopped

    @property
    def defunct(self):
        return self._defunct

    @property
    def alive(self):
        return self._started and not self._stopped

    @property
    def status(self):
        """One character status for this node. """
        if self._defunct:
            return '!'
        if not self.started:
            return ' '
        if not self.stopped:
            return '+'
        return '-'

    def __init__(self, wrapped, parent, services=None):
        super().__init__(wrapped)

        self.parent = parent

        if services:
            if parent:
                raise RuntimeError(
                    'Having services defined both in GraphExecutionContext and child NodeExecutionContext is not supported, for now.'
                )
            self.services = create_container(services)
        else:
            self.services = None

        self._started, self._stopped, self._defunct = False, False, False
        self._stack = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.stop()

    def start(self):
        if self.started:
            raise RuntimeError('Cannot start a node twice ({}).'.format(get_name(self)))

        self._started = True

        try:
            self._stack = ContextCurrifier(self.wrapped, *self._get_initial_context())
            if isconfigurabletype(self.wrapped):
                # Not normal to have a partially configured object here, so let's warn the user instead of having get into
                # the hard trouble of understanding that by himself.
                raise TypeError(
                    'The Configurable should be fully instanciated by now, unfortunately I got a PartiallyConfigured object...'
                )
            self._stack.setup(self)
        except Exception:
            return self.fatal(sys.exc_info())

    def loop(self):
        """Generic loop. A bit boring. """
        while self.alive:
            self.step()

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

    def _get_initial_context(self):
        if self.parent:
            return self.parent.services.args_for(self.wrapped)
        if self.services:
            return self.services.args_for(self.wrapped)
        return ()

    def handle_error(self, exctype, exc, tb, *, level=logging.ERROR):
        logging.getLogger(__name__).log(level, repr(self), exc_info=(exctype, exc, tb))

    def fatal(self, exc_info):
        self._defunct = True
        self.input.shutdown()
        self.handle_error(*exc_info, level=logging.CRITICAL)
