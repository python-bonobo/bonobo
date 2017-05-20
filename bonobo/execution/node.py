import traceback
from queue import Empty
from time import sleep

from bonobo.constants import INHERIT_INPUT, NOT_MODIFIED
from bonobo.errors import InactiveReadableError
from bonobo.execution.base import LoopingExecutionContext
from bonobo.structs.bags import Bag
from bonobo.structs.inputs import Input
from bonobo.util.compat import deprecated_alias
from bonobo.util.errors import is_error
from bonobo.util.iterators import iter_if_not_sequence
from bonobo.util.objects import get_name
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

    def __init__(self, wrapped, parent=None, services=None):
        LoopingExecutionContext.__init__(self, wrapped, parent=parent, services=services)
        WithStatistics.__init__(self, 'in', 'out', 'err')

        self.input = Input()
        self.outputs = []

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

        if is_error(value):
            value.apply(self.handle_error)
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
        try:
            results = iter_if_not_sequence(results)
        except TypeError:  # not an iterator
            if results:
                self.send(_resolve(input_bag, results))
            else:
                # case with no result, an execution went through anyway, use for stats.
                # self._exec_count += 1
                pass
        else:
            while True:  # iterator
                try:
                    result = next(results)
                except StopIteration:
                    break
                else:
                    self.send(_resolve(input_bag, result))


def _resolve(input_bag, output):
    # NotModified means to send the input unmodified to output.
    if output is NOT_MODIFIED:
        return input_bag

    if is_error(output):
        return output

    # If it does not look like a bag, let's create one for easier manipulation
    if hasattr(output, 'apply'):
        # Already a bag? Check if we need to set parent.
        if INHERIT_INPUT in output.flags:
            output.set_parent(input_bag)
    else:
        # Not a bag? Let's encapsulate it.
        output = Bag(output)

    return output
