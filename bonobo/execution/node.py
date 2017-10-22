import traceback
from queue import Empty
from time import sleep
from types import GeneratorType

from bonobo import settings
from bonobo.constants import INHERIT_INPUT, NOT_MODIFIED, BEGIN, END
from bonobo.errors import InactiveReadableError, UnrecoverableError
from bonobo.execution.base import LoopingExecutionContext
from bonobo.structs.bags import Bag
from bonobo.structs.inputs import Input
from bonobo.util import get_name, iserrorbag, isloopbackbag, isdict, istuple
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
            self.input.put(message)

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


def _resolve(input_bag, output):
    # NotModified means to send the input unmodified to output.
    if output is NOT_MODIFIED:
        return input_bag

    if iserrorbag(output):
        return output

    # If it does not look like a bag, let's create one for easier manipulation
    if hasattr(output, 'apply'):  # XXX TODO use isbag() ?
        # Already a bag? Check if we need to set parent.
        if INHERIT_INPUT in output.flags:
            output.set_parent(input_bag)
        return output

    # If we're using kwargs ioformat, then a dict means kwargs.
    if settings.IOFORMAT == settings.IOFORMAT_KWARGS and isdict(output):
        return Bag(**output)

    if istuple(output):
        if len(output) > 1 and isdict(output[-1]):
            return Bag(*output[0:-1], **output[-1])
        return Bag(*output)

    # Either we use arg0 format, either it's "just" a value.
    return Bag(output)
