import logging
import sys
from contextlib import contextmanager
from logging import ERROR

from mondrian import term

from bonobo.util import deprecated
from bonobo.util.objects import Wrapper, get_name


@contextmanager
def recoverable(error_handler):
    try:
        yield
    except Exception:  # pylint: disable=broad-except
        error_handler(*sys.exc_info(), level=ERROR)


@contextmanager
def unrecoverable(error_handler):
    try:
        yield
    except Exception:  # pylint: disable=broad-except
        error_handler(*sys.exc_info(), level=ERROR)
        raise  # raise unrecoverableerror from x ?


class Lifecycle:
    def __init__(self):
        self._started = False
        self._stopped = False
        self._killed = False
        self._defunct = False

    @property
    def started(self):
        return self._started

    @property
    def stopped(self):
        return self._stopped

    @property
    def killed(self):
        return self._killed

    @property
    def defunct(self):
        return self._defunct

    @property
    def alive(self):
        return self._started and not self._stopped

    @property
    def should_loop(self):
        # TODO XXX started/stopped?
        return not any((self.defunct, self.killed))

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

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.stop()

    def get_flags_as_string(self):
        if self._defunct:
            return term.red('[defunct]')
        if self.killed:
            return term.lightred('[killed]')
        if self.stopped:
            return term.lightblack('[done]')
        return ''

    def start(self):
        if self.started:
            raise RuntimeError('This context is already started ({}).'.format(get_name(self)))

        self._started = True

    def stop(self):
        if not self.started:
            raise RuntimeError('This context cannot be stopped as it never started ({}).'.format(get_name(self)))

        self._stopped = True

        if self._stopped:  # Stopping twice has no effect
            return

    def kill(self):
        if not self.started:
            raise RuntimeError('Cannot kill an unstarted context.')

        if self.stopped:
            raise RuntimeError('Cannot kill a stopped context.')

        self._killed = True

    @deprecated
    def handle_error(self, exctype, exc, tb, *, level=logging.ERROR):
        return self.error((exctype, exc, tb), level=level)

    def error(self, exc_info, *, level=logging.ERROR):
        logging.getLogger(__name__).log(level, repr(self), exc_info=exc_info)

    def fatal(self, exc_info, *, level=logging.CRITICAL):
        logging.getLogger(__name__).log(level, repr(self), exc_info=exc_info)
        self._defunct = True

    def as_dict(self):
        return {
            'status': self.status,
            'name': self.name,
            'stats': self.get_statistics_as_string(),
            'flags': self.get_flags_as_string(),
        }


class BaseContext(Lifecycle, Wrapper):
    def __init__(self, wrapped, *, parent=None):
        Lifecycle.__init__(self)
        Wrapper.__init__(self, wrapped)
        self.parent = parent
