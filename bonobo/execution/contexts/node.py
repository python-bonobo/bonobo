import logging
import sys
from collections import namedtuple
from queue import Empty
from time import sleep
from types import GeneratorType

from bonobo.config import create_container
from bonobo.config.processors import ContextCurrifier
from bonobo.constants import BEGIN, END, INHERIT, NOT_MODIFIED, TICK_PERIOD, Flag, Token
from bonobo.errors import InactiveReadableError, UnrecoverableError, UnrecoverableTypeError
from bonobo.execution.contexts.base import BaseContext
from bonobo.structs.inputs import Input
from bonobo.util import ensure_tuple, get_name, isconfigurabletype
from bonobo.util.bags import BagType
from bonobo.util.statistics import WithStatistics

logger = logging.getLogger(__name__)

UnboundArguments = namedtuple('UnboundArguments', ['args', 'kwargs'])


class NodeExecutionContext(BaseContext, WithStatistics):
    def __init__(self, wrapped, *, parent=None, services=None, _input=None, _outputs=None):
        """
        Node execution context has the responsibility fo storing the state of a transformation during its execution.

        :param wrapped: wrapped transformation
        :param parent: parent context, most probably a graph context
        :param services: dict-like collection of services
        :param _input: input queue (optional)
        :param _outputs: output queues (optional)
        """
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

        # Types
        self._input_type, self._input_length = None, None
        self._output_type = None

        # Stack: context decorators for the execution
        self._stack = None

    def __str__(self):
        return self.__name__ + self.get_statistics_as_string(prefix=' ')

    def __repr__(self):
        name, type_name = get_name(self), get_name(type(self))
        return '<{}({}{}){}>'.format(type_name, self.status, name, self.get_statistics_as_string(prefix=' '))

    def start(self):
        """
        Starts this context, a.k.a the phase where you setup everything which will be necessary during the whole
        lifetime of a transformation.

        The "ContextCurrifier" is in charge of setting up a decorating stack, that includes both services and context
        processors, and will call the actual node callable with additional parameters.

        """
        super().start()

        try:
            initial = self._get_initial_context()
            self._stack = ContextCurrifier(self.wrapped, *initial.args, **initial.kwargs)
            if isconfigurabletype(self.wrapped):
                # Not normal to have a partially configured object here, so let's warn the user instead of having get into
                # the hard trouble of understanding that by himself.
                raise TypeError(
                    'Configurables should be instanciated before execution starts.\nGot {!r}.\n'.format(self.wrapped)
                )
            self._stack.setup(self)
        except Exception:
            # Set the logging level to the lowest possible, to avoid double log.
            self.fatal(sys.exc_info(), level=0)

            # We raise again, so the error is not ignored out of execution loops.
            raise

    def loop(self):
        """
        The actual infinite loop for this transformation.

        """
        logger.debug('Node loop starts for {!r}.'.format(self))

        while self.should_loop:
            try:
                self.step()
            except InactiveReadableError:
                break
            except Empty:
                sleep(TICK_PERIOD)  # XXX: How do we determine this constant?
                continue
            except (NotImplementedError, UnrecoverableError):
                self.fatal(sys.exc_info())  # exit loop
            except Exception:  # pylint: disable=broad-except
                self.error(sys.exc_info())  # does not exit loop
            except BaseException:
                self.fatal(sys.exc_info())  # exit loop

        logger.debug('Node loop ends for {!r}.'.format(self))

    def step(self):
        """
        A single step in the loop.

        Basically gets an input bag, send it to the node, interpret the results.

        """

        # Pull and check data
        input_bag = self._get()

        # Sent through the stack
        results = self._stack(input_bag)

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
                else:
                    # Push data (in case of an iterator)
                    self._send(self._cast(input_bag, result))
        elif results:
            # Push data (returned value)
            self._send(self._cast(input_bag, results))
        else:
            # case with no result, an execution went through anyway, use for stats.
            # self._exec_count += 1
            pass

    def stop(self):
        """
        Cleanup the context, after the loop ended.

        """
        if self._stack:
            try:
                self._stack.teardown()
            except Exception:
                self.fatal(sys.exc_info())

        super().stop()

    def send(self, *_output, _input=None):
        return self._send(self._cast(_input, _output))

    ### Input type and fields
    @property
    def input_type(self):
        return self._input_type

    def set_input_type(self, input_type):
        if self._input_type is not None:
            raise RuntimeError('Cannot override input type, already have %r.', self._input_type)

        if not isinstance(input_type, type):
            raise UnrecoverableTypeError('Input types must be regular python types.')

        if not issubclass(input_type, tuple):
            raise UnrecoverableTypeError('Input types must be subclasses of tuple (and act as tuples).')

        self._input_type = input_type

    def get_input_fields(self):
        return self._input_type._fields if self._input_type and hasattr(self._input_type, '_fields') else None

    def set_input_fields(self, fields, typename='Bag'):
        self.set_input_type(BagType(typename, fields))

    ### Output type and fields
    @property
    def output_type(self):
        return self._output_type

    def set_output_type(self, output_type):
        if self._output_type is not None:
            raise RuntimeError('Cannot override output type, already have %r.', self._output_type)

        if type(output_type) is not type:
            raise UnrecoverableTypeError('Output types must be regular python types.')

        if not issubclass(output_type, tuple):
            raise UnrecoverableTypeError('Output types must be subclasses of tuple (and act as tuples).')

        self._output_type = output_type

    def get_output_fields(self):
        return self._output_type._fields if self._output_type and hasattr(self._output_type, '_fields') else None

    def set_output_fields(self, fields, typename='Bag'):
        self.set_output_type(BagType(typename, fields))

    ### Attributes
    def setdefault(self, attr, value):
        try:
            getattr(self, attr)
        except AttributeError:
            setattr(self, attr, value)

    def write(self, *messages):
        """
        Push a message list to this context's input queue.

        :param mixed value: message
        """
        for message in messages:
            if isinstance(message, Token):
                self.input.put(message)
            elif self._input_type:
                self.input.put(ensure_tuple(message, cls=self._input_type))
            else:
                self.input.put(ensure_tuple(message))

    def write_sync(self, *messages):
        self.write(BEGIN, *messages, END)
        for _ in messages:
            self.step()

    def error(self, exc_info, *, level=logging.ERROR):
        self.increment('err')
        super().error(exc_info, level=level)

    def fatal(self, exc_info, *, level=logging.CRITICAL):
        self.increment('err')
        super().fatal(exc_info, level=level)
        self.input.shutdown()

    def get_service(self, name):
        if self.parent:
            return self.parent.services.get(name)
        return self.services.get(name)

    def _get(self):
        """
        Read from the input queue.

        If Queue raises (like Timeout or Empty), stat won't be changed.

        """
        input_bag = self.input.get()

        # Store or check input type
        if self._input_type is None:
            self._input_type = type(input_bag)
        elif type(input_bag) is not self._input_type:
            raise UnrecoverableTypeError(
                'Input type changed between calls to {!r}.\nGot {!r} which is not of type {!r}.'.format(
                    self.wrapped, input_bag, self._input_type
                )
            )

        # Store or check input length, which is a soft fallback in case we're just using tuples
        if self._input_length is None:
            self._input_length = len(input_bag)
        elif len(input_bag) != self._input_length:
            raise UnrecoverableTypeError(
                'Input length changed between calls to {!r}.\nExpected {} but got {}: {!r}.'.format(
                    self.wrapped, self._input_length, len(input_bag), input_bag
                )
            )

        self.increment('in')  # XXX should that go before type check ?

        return input_bag

    def _cast(self, _input, _output):
        """
        Transforms a pair of input/output into the real slim output.

        :param _input: Bag
        :param _output: mixed
        :return: Bag
        """

        tokens, _output = split_token(_output)

        if NOT_MODIFIED in tokens:
            return ensure_tuple(_input, cls=(self.output_type or tuple))

        if INHERIT in tokens:
            if self._output_type is None:
                self._output_type = concat_types(self._input_type, self._input_length, self._output_type, len(_output))
            _output = _input + ensure_tuple(_output)

        return ensure_tuple(_output, cls=(self._output_type or tuple))

    def _send(self, value, _control=False):
        """
        Sends a message to all of this context's outputs.

        :param mixed value: message
        :param _control: if true, won't count in statistics.
        """

        if not _control:
            self.increment('out')

        for output in self.outputs:
            output.put(value)

    def _get_initial_context(self):
        if self.parent:
            return UnboundArguments((), self.parent.services.kwargs_for(self.wrapped))
        if self.services:
            return UnboundArguments((), self.services.kwargs_for(self.wrapped))
        return UnboundArguments((), {})


def isflag(param):
    return isinstance(param, Flag)


def split_token(output):
    """
    Split an output into token tuple, real output tuple.

    :param output:
    :return: tuple, tuple
    """

    output = ensure_tuple(output)

    flags, i, len_output, data_allowed = set(), 0, len(output), True
    while i < len_output and isflag(output[i]):
        if output[i].must_be_first and i:
            raise ValueError('{} flag must be first.'.format(output[i]))
        if i and output[i - 1].must_be_last:
            raise ValueError('{} flag must be last.'.format(output[i - 1]))
        if output[i] in flags:
            raise ValueError('Duplicate flag {}.'.format(output[i]))
        flags.add(output[i])
        data_allowed &= output[i].allows_data
        i += 1

    output = output[i:]
    if not data_allowed and len(output):
        raise ValueError('Output data provided after a flag that does not allow data.')
    return flags, output


def concat_types(t1, l1, t2, l2):
    t1, t2 = t1 or tuple, t2 or tuple

    if t1 == t2 == tuple:
        return tuple

    f1 = t1._fields if hasattr(t1, '_fields') else tuple(range(l1))
    f2 = t2._fields if hasattr(t2, '_fields') else tuple(range(l2))

    return BagType('Inherited', f1 + f2)
