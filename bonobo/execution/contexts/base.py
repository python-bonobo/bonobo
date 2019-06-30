import logging
import sys
from contextlib import contextmanager

from mondrian import term

from bonobo.util import deprecated
from bonobo.util.objects import Wrapper, get_name


@contextmanager
def recoverable(error_handler):
    try:
        yield
    except Exception:  # pylint: disable=broad-except
        error_handler(*sys.exc_info(), level=logging.ERROR)


@contextmanager
def unrecoverable(error_handler):
    try:
        yield
    except Exception:  # pylint: disable=broad-except
        error_handler(*sys.exc_info(), level=logging.ERROR)
        raise  # raise unrecoverableerror from x ?


class Lifecycle:
    def __init__(self, *, daemon=False):
        # Daemonized? (lifecycle is equal to execution, not to its own)
        self._daemon = bool(daemon)

        self._started = False
        self._stopped = False
        self._killed = False
        self._defunct = False

    @property
    def daemon(self):
        return self._daemon

    @property
    def started(self):
        """
        Is this context started?

        """
        return self._daemon or self._started

    @property
    def stopped(self):
        """
        Is this context stopped?

        """
        return not self._daemon and self._stopped

    @property
    def killed(self):
        """
        Is this context marked as killed?

        """
        return self._killed

    @property
    def defunct(self):
        """
        Is this context marked as defunct? This happens after an unrecoverable error was raised in a node.
        """
        return self._defunct

    @property
    def alive(self):
        """
        Is this context alive? It means it should be started, but not yet stopped.

        """
        return self.daemon or (self._started and not self._stopped)

    @property
    def should_loop(self):
        """
        Should we run the execution context loop, or does the current state means that we should give up on execution?

        """
        return self.alive and not any((self.defunct, self.killed))

    @property
    def status(self):
        """
        One character status for this node, used for display.

        """
        if self._defunct:
            return "!"
        if self.daemon:
            return "~"
        if not self.started:
            return " "
        if not self.stopped:
            return "+"
        return "-"

    def __enter__(self):
        """
        Allows to enter this context like a context manager (using `with ...` statement).

        """
        self.start()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):  # lgtm [py/special-method-wrong-signature]
        """
        Allows to exit this context when used as a context manager.

        """
        self.stop()

    def get_flags_as_string(self):
        """
        Utility function used to display verbose and explicit status in the console.

        """
        if self._defunct:
            return term.red("[defunct]")
        if self.killed:
            return term.lightred("[killed]")
        if self.stopped:
            return term.lightblack("[done]")
        return ""

    def start(self):
        """
        Starts this context. This can only be done once.

        """
        if self.daemon:
            return

        if self.started:
            raise RuntimeError("This context is already started ({}).".format(get_name(self)))

        self._started = True

    def stop(self):
        """
        Stops this context. The context must be started first, but once it is, you can call this method as many time
        as you want, the subsequent calls will have no effect.

        """
        if not self.started:
            raise RuntimeError("This context cannot be stopped as it never started ({}).".format(get_name(self)))

        self._stopped = True

    def daemonize(self, daemon=True):
        self._daemon = bool(daemon)

    def kill(self):
        """
        Kills a running context. This only sets a flag that will be used by the loop control structures to actually
        stop the work in a clean manner.

        """
        if not self.started:
            raise RuntimeError("Cannot kill an unstarted context.")

        if self.stopped:
            raise RuntimeError("Cannot kill a stopped context.")

        self._killed = True

    @deprecated
    def handle_error(self, exctype, exc, tb, *, level=logging.ERROR):
        return self.error((exctype, exc, tb), level=level)

    def error(self, exc_info, *, level=logging.ERROR):
        """
        Called when a non-fatal error happens.

        """
        logging.getLogger(__name__).log(level, repr(self), exc_info=exc_info)

    def fatal(self, exc_info, *, level=logging.CRITICAL):
        """
        Called when a fatal/unrecoverable error happens.

        """
        logging.getLogger(__name__).log(level, repr(self), exc_info=exc_info)
        self._defunct = True

    def as_dict(self):
        """
        Returns a dict describing this context, that can be used for example for JSON serialization.
        """
        return {
            "status": self.status,
            "name": self.name,
            "stats": self.get_statistics_as_string(),
            "flags": self.get_flags_as_string(),
        }


class BaseContext(Lifecycle, Wrapper):
    def __init__(self, wrapped, *, daemon=False, parent=None):
        Lifecycle.__init__(self, daemon=daemon)
        Wrapper.__init__(self, wrapped)
        self.parent = parent

    @property
    def xstatus(self):
        """
        UNIX-like exit status, only coherent if the context has stopped.

        """
        if self._defunct:
            return 70
        return 0
