import logging
import sys
from queue import Empty
from time import sleep
from types import GeneratorType

from bonobo.config import create_container
from bonobo.config.processors import ContextCurrifier
from bonobo.constants import NOT_MODIFIED, BEGIN, END, TICK_PERIOD
from bonobo.errors import InactiveReadableError, UnrecoverableError
from bonobo.execution.contexts.base import BaseContext
from bonobo.structs.bags import Bag
from bonobo.structs.inputs import Input
from bonobo.structs.tokens import Token
from bonobo.util import get_name, iserrorbag, isloopbackbag, isbag, istuple, isconfigurabletype
from bonobo.util.statistics import WithStatistics

logger = logging.getLogger(__name__)


class NodeExecutionContext(BaseContext, WithStatistics):
    def __init__(self, wrapped, *, parent=None, services=None, _input=None, _outputs=None):
        BaseContext.__init__(self, wrapped, parent=parent)
        WithStatistics.__init__(self, 'in', 'out', 'err', 'warn')

        # Services: how we'll access external dependencies
        if services:
            if self.parent:
                raise RuntimeError(
                    'Having services defined both in GraphExecutionContext and child NodeExecutionContext is not supported, for now.'
                )
            self.services = create_container(services)
        else:
            self.services = None

        # Input / Output: how the wrapped node will communicate
        self.input = _input or Input()
        self.outputs = _outputs or []

        # Stack: context decorators for the execution
        self._stack = None

    def __str__(self):
        return self.__name__ + self.get_statistics_as_string(prefix=' ')

    def __repr__(self):
        name, type_name = get_name(self), get_name(type(self))
        return '<{}({}{}){}>'.format(type_name, self.status, name, self.get_statistics_as_string(prefix=' '))

    def start(self):
        super().start()

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
        logger.debug('Node loop starts for {!r}.'.format(self))
        while self.should_loop:
            try:
                self.step()
            except InactiveReadableError:
                break
            except Empty:
                sleep(TICK_PERIOD)  # XXX: How do we determine this constant?
                continue
            except UnrecoverableError:
                self.handle_error(*sys.exc_info())
                self.input.shutdown()
                break
            except Exception:  # pylint: disable=broad-except
                self.handle_error(*sys.exc_info())
            except BaseException:
                self.handle_error(*sys.exc_info())
                break
        logger.debug('Node loop ends for {!r}.'.format(self))

    def step(self):
        """Runs a transformation callable with given args/kwargs and flush the result into the right
        output channel."""

        # Pull data
        input_bag = self.get()

        # Sent through the stack
        try:
            results = input_bag.apply(self._stack)
        except Exception:
            return self.handle_error(*sys.exc_info())

        # self._exec_time += timer.duration
        # Put data onto output channels

        if isinstance(results, GeneratorType):
            while True:
                try:
                    # if kill flag was step, stop iterating.
                    if self._killed:
                        break
                    result = next(results)
                except StopIteration:
                    # That's not an error, we're just done.
                    break
                except Exception:
                    # Let's kill this loop, won't be able to generate next.
                    self.handle_error(*sys.exc_info())
                    break
                else:
                    self.send(_resolve(input_bag, result))
        elif results:
            self.send(_resolve(input_bag, results))
        else:
            # case with no result, an execution went through anyway, use for stats.
            # self._exec_count += 1
            pass

    def stop(self):
        if self._stack:
            self._stack.teardown()

        super().stop()

    def handle_error(self, exctype, exc, tb, *, level=logging.ERROR):
        self.increment('err')
        logging.getLogger(__name__).log(level, repr(self), exc_info=(exctype, exc, tb))

    def fatal(self, exc_info, *, level=logging.CRITICAL):
        super().fatal(exc_info, level=level)
        self.input.shutdown()

    def write(self, *messages):
        """
        Push a message list to this context's input queue.

        :param mixed value: message
        """
        for message in messages:
            self.input.put(message if isinstance(message, (Bag, Token)) else Bag(message))

    def write_sync(self, *messages):
        self.write(BEGIN, *messages, END)
        for _ in messages:
            self.step()

    def send(self, value, _control=False):
        """
        Sends a message to all of this context's outputs.

        :param mixed value: message
        :param _control: if true, won't count in statistics.
        """

        if not _control:
            self.increment('out')

        if iserrorbag(value):
            value.apply(self.handle_error)
        elif isloopbackbag(value):
            self.input.put(value)
        else:
            for output in self.outputs:
                output.put(value)

    def get(self):
        """
        Get from the queue first, then increment stats, so if Queue raise Timeout or Empty, stat won't be changed.

        """
        row = self.input.get()  # XXX TIMEOUT ???
        self.increment('in')
        return row

    def _get_initial_context(self):
        if self.parent:
            return self.parent.services.args_for(self.wrapped)
        if self.services:
            return self.services.args_for(self.wrapped)
        return ()


def isflag(param):
    return isinstance(param, Token) and param in (NOT_MODIFIED, )


def split_tokens(output):
    """
    Split an output into token tuple, real output tuple.

    :param output:
    :return: tuple, tuple
    """
    if isinstance(output, Token):
        # just a flag
        return (output, ), ()

    if not istuple(output):
        # no flag
        return (), (output, )

    i = 0
    while isflag(output[i]):
        i += 1

    return output[:i], output[i:]


def _resolve(input_bag, output):
    """
    This function is key to how bonobo works (and internal, too). It transforms a pair of input/output into what is the
    real output.

    :param input_bag: Bag
    :param output: mixed
    :return: Bag
    """
    if isbag(output):
        return output

    tokens, output = split_tokens(output)

    if len(tokens) == 1 and tokens[0] is NOT_MODIFIED:
        return input_bag

    return output if isbag(output) else Bag(output)
