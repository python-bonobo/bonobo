import traceback
from time import sleep

from bonobo.config import Container
from bonobo.config.processors import resolve_processors
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

        self._started, self._stopped, self._context, self._stack = False, False, None, []

    def start(self):
        assert self.state == (False,
                              False), ('{}.start() can only be called on a new node.').format(type(self).__name__)
        assert self._context is None
        self._started = True

        if self.parent:
            self._context = self.parent.services.args_for(self.wrapped)
        elif self.services:
            self._context = self.services.args_for(self.wrapped)
        else:
            self._context = ()

        for processor in resolve_processors(self.wrapped):
            try:
                _processed = processor(self.wrapped, self, *self._context)
                _append_to_context = next(_processed)
                if _append_to_context is not None:
                    self._context += ensure_tuple(_append_to_context)
            except Exception as exc:  # pylint: disable=broad-except
                self.handle_error(exc, traceback.format_exc())
                raise
            self._stack.append(_processed)

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
        if self._context is not None:
            while len(self._stack):
                processor = self._stack.pop()
                try:
                    # todo yield from ? how to ?
                    next(processor)
                except StopIteration as exc:
                    # This is normal, and wanted.
                    pass
                except Exception as exc:  # pylint: disable=broad-except
                    self.handle_error(exc, traceback.format_exc())
                    raise
                else:
                    # No error ? We should have had StopIteration ...
                    raise RuntimeError('Context processors should not yield more than once.')

    def handle_error(self, exc, trace):
        return print_error(exc, trace, context=self.wrapped)
