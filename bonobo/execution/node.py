import traceback
from queue import Empty
from time import sleep

from bonobo.constants import INHERIT_INPUT, NOT_MODIFIED
from bonobo.core.inputs import Input
from bonobo.core.statistics import WithStatistics
from bonobo.errors import InactiveReadableError
from bonobo.execution.base import LoopingExecutionContext
from bonobo.structs.bags import Bag
from bonobo.util.errors import is_error
from bonobo.util.iterators import iter_if_not_sequence


class NodeExecutionContext(WithStatistics, LoopingExecutionContext):
    """
    todo: make the counter dependant of parent context?
    """

    @property
    def alive(self):
        """todo check if this is right, and where it is used"""
        return self.input.alive and self._started and not self._stopped

    def __init__(self, wrapped, parent=None, services=None):
        LoopingExecutionContext.__init__(self, wrapped, parent=parent, services=services)
        WithStatistics.__init__(self, 'in', 'out', 'err')

        self.input = Input()
        self.outputs = []

    def __str__(self):
        return (('+' if self.alive else '-') + ' ' + self.__name__ + ' ' + self.get_statistics_as_string()).strip()

    def __repr__(self):
        stats = self.get_statistics_as_string().strip()
        return '<{}({}{}){}>'.format(
            type(self).__name__,
            '+' if self.alive else '',
            self.__name__,
            (' ' + stats) if stats else '',
        )

    def recv(self, *messages):
        """
        Push a message list to this context's input queue.

        :param mixed value: message
        """
        for message in messages:
            self.input.put(message)

    def send(self, value, _control=False):
        """
        Sends a message to all of this context's outputs.

        :param mixed value: message
        :param _control: if true, won't count in statistics.
        """
        if not _control:
            self.increment('out')
        for output in self.outputs:
            output.put(value)

    def get(self):
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
        self.handle_results(input_bag, input_bag.apply(self.wrapped, *self._context))

    def push(self, bag):
        # MAKE THIS PUBLIC API FOR CONTEXT PROCESSORS !!!
        # xxx handle error or send in first call to apply(...)?
        # xxx return value ?
        bag.apply(self.handle_error) if is_error(bag) else self.send(bag)

    def handle_results(self, input_bag, results):
        # self._exec_time += timer.duration
        # Put data onto output channels
        try:
            results = iter_if_not_sequence(results)
        except TypeError:  # not an iterator
            if results:
                self.push(_resolve(input_bag, results))
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
                    self.push(_resolve(input_bag, result))


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
