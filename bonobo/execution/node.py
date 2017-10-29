import traceback
from queue import Empty
from time import sleep
from types import GeneratorType

from bonobo.constants import NOT_MODIFIED, BEGIN, END
from bonobo.errors import InactiveReadableError, UnrecoverableError
from bonobo.execution.base import LoopingExecutionContext
from bonobo.structs.bags import Bag
from bonobo.structs.inputs import Input
from bonobo.structs.tokens import Token
from bonobo.util import get_name, iserrorbag, isloopbackbag, isbag, istuple
from bonobo.util.compat import deprecated_alias
from bonobo.util.statistics import WithStatistics


class NodeExecutionContext(WithStatistics, LoopingExecutionContext):
    """
    todo: make the counter dependant of parent context?
    """

    @property
    def alive(self):
        """todo check if this is right, and where it is used"""
        return self._started and not self._stopped

    @property
    def alive_str(self):
        return '+' if self.alive else '-'

    def __init__(self, wrapped, parent=None, services=None, _input=None, _outputs=None):
        LoopingExecutionContext.__init__(self, wrapped, parent=parent, services=services)
        WithStatistics.__init__(self, 'in', 'out', 'err')

        self.input = _input or Input()
        self.outputs = _outputs or []

    def __str__(self):
        return self.alive_str + ' ' + self.__name__ + self.get_statistics_as_string(prefix=' ')

    def __repr__(self):
        name, type_name = get_name(self), get_name(type(self))
        return '<{}({}{}){}>'.format(type_name, self.alive_str, name, self.get_statistics_as_string(prefix=' '))

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

    # XXX deprecated alias
    recv = deprecated_alias('recv', write)

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

    push = deprecated_alias('push', send)

    def get(self):  # recv() ? input_data = self.receive()
        """
        Get from the queue first, then increment stats, so if Queue raise Timeout or Empty, stat won't be changed.

        """
        row = self.input.get(timeout=self.PERIOD)
        self.increment('in')
        return row

    def loop(self):
        while True:
            try:
                self.step()
            except KeyboardInterrupt:
                raise
            except InactiveReadableError:
                break
            except Empty:
                sleep(self.PERIOD)
                continue
            except UnrecoverableError as exc:
                self.handle_error(exc, traceback.format_exc())
                self.input.shutdown()
                break
            except Exception as exc:  # pylint: disable=broad-except
                self.handle_error(exc, traceback.format_exc())

    def step(self):
        # Pull data from the first available input channel.
        """Runs a transformation callable with given args/kwargs and flush the result into the right
        output channel."""

        input_bag = self.get()

        # todo add timer
        self.handle_results(input_bag, input_bag.apply(self._stack))

    def handle_results(self, input_bag, results):
        # self._exec_time += timer.duration
        # Put data onto output channels

        if isinstance(results, GeneratorType):
            while True:
                try:
                    result = next(results)
                except StopIteration:
                    break
                else:
                    self.send(_resolve(input_bag, result))
        elif results:
            self.send(_resolve(input_bag, results))
        else:
            # case with no result, an execution went through anyway, use for stats.
            # self._exec_count += 1
            pass


def isflag(param):
    return isinstance(param, Token) and param in (NOT_MODIFIED,)


def split_tokens(output):
    """
    Split an output into token tuple, real output tuple.

    :param output:
    :return: tuple, tuple
    """
    if isinstance(output, Token):
        # just a flag
        return (output,), ()

    if not istuple(output):
        # no flag
        return (), (output,)

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
