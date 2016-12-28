import traceback
from functools import partial
from queue import Empty
from time import sleep

from bonobo.core.bags import Bag, INHERIT_INPUT
from bonobo.core.errors import InactiveReadableError
from bonobo.core.inputs import Input
from bonobo.core.stats import WithStatistics
from bonobo.util.lifecycle import get_initializer, get_finalizer
from bonobo.util.tokens import BEGIN, END, NEW, RUNNING, TERMINATED, NOT_MODIFIED


class ExecutionContext:
    def __init__(self, graph, plugins=None):
        self.graph = graph
        self.components = [ComponentExecutionContext(component, self) for component in self.graph.components]

        self.plugins = [PluginExecutionContext(plugin, parent=self) for plugin in plugins or ()]

        for i, component_context in enumerate(self):
            try:
                component_context.outputs = [self[j].input for j in self.graph.outputs_of(i)]
            except KeyError:
                continue
            component_context.input.on_begin = partial(component_context.send, BEGIN, _control=True)
            component_context.input.on_end = partial(component_context.send, END, _control=True)

    def __getitem__(self, item):
        return self.components[item]

    def __len__(self):
        return len(self.components)

    def __iter__(self):
        yield from self.components

    def recv(self, *messages):
        """Push a list of messages in the inputs of this graph's inputs, matching the output of special node "BEGIN" in
        our graph."""

        for i in self.graph.outputs_of(BEGIN):
            for message in messages:
                self[i].recv(message)

    @property
    def alive(self):
        return any(component.alive for component in self.components)


class AbstractLoopContext:
    alive = True
    PERIOD = 0.25

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def run(self):
        self.initialize()
        self.loop()
        self.finalize()

    def initialize(self):
        # pylint: disable=broad-except
        try:
            get_initializer(self.wrapped)(self)
        except Exception as exc:
            self.handle_error(exc, traceback.format_exc())

    def loop(self):
        """Generic loop. A bit boring. """
        while self.alive:
            self._loop()
            sleep(self.PERIOD)

    def _loop(self):
        """
        TODO xxx this is a step, not a loop
        """
        raise NotImplementedError('Abstract.')

    def finalize(self):
        """Generic finalizer. """
        # pylint: disable=broad-except
        try:
            get_finalizer(self.wrapped)(self)
        except Exception as exc:
            self.handle_error(exc, traceback.format_exc())

    def handle_error(self, exc, trace):
        """
        Error handler. Whatever happens in a plugin or component, if it looks like an exception, taste like an exception
        or somehow make me think it is an exception, I'll handle it.

        :param exc: the culprit
        :param trace: Hercule Poirot's logbook.
        :return: to hell
        """

        from blessings import Terminal
        term = Terminal()
        print(term.bold(term.red('\U0001F4A3 {} in {}'.format(type(exc).__name__, self.wrapped))))
        print(trace)


class PluginExecutionContext(AbstractLoopContext):
    def __init__(self, plugin, parent):
        self.plugin = plugin
        self.parent = parent
        super().__init__(self.plugin)

    def shutdown(self):
        self.alive = False

    def _loop(self):
        try:
            self.wrapped.run(self)
        except Exception as exc:  # pylint: disable=broad-except
            self.handle_error(exc, traceback.format_exc())


class ComponentExecutionContext(WithStatistics, AbstractLoopContext):
    """
    todo: make the counter dependant of parent context?
    """

    @property
    def alive(self):
        """todo check if this is right, and where it is used"""
        return self.input.alive

    @property
    def name(self):
        return getattr(self.component, '__name__', getattr(type(self.component), '__name__', repr(self.component)))

    def __init__(self, component, parent):
        self.parent = parent
        self.component = component
        self.input = Input()
        self.outputs = []
        self.state = NEW
        self.stats = {
            'in': 0,
            'out': 0,
            'err': 0,
            'read': 0,
            'write': 0,
        }

        super().__init__(self.component)

    def __repr__(self):
        """Adds "alive" information to the transform representation."""
        return ('+' if self.alive else '-') + ' ' + self.name + ' ' + self.get_stats_as_string()

    def get_stats(self, *args, **kwargs):
        return (
            (
                'in',
                self.stats['in'], ),
            (
                'out',
                self.stats['out'], ),
            (
                'err',
                self.stats['err'], ), )

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
            self.stats['out'] += 1
        for output in self.outputs:
            output.put(value)

    def get(self):
        """
        Get from the queue first, then increment stats, so if Queue raise Timeout or Empty, stat won't be changed.

        """
        row = self.input.get(timeout=self.PERIOD)
        self.stats['in'] += 1
        return row

    def _call(self, bag):
        # todo add timer
        if getattr(self.component, '_with_context', False):
            return bag.apply(self.component, self)
        return bag.apply(self.component)

    def initialize(self):
        # pylint: disable=broad-except
        assert self.state is NEW, ('A {} can only be run once, and thus is expected to be in {} state at '
                                   'initialization time.').format(type(self).__name__, NEW)
        self.state = RUNNING
        super().initialize()

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
        outputs = self._call(input_bag)

        # self._exec_time += timer.duration
        # Put data onto output channels
        try:
            outputs = _iter(outputs)
        except TypeError:
            if outputs:
                self.send(_resolve(input_bag, outputs))
            else:
                # case with no result, an execution went through anyway, use for stats.
                # self._exec_count += 1
                pass
        else:
            while True:
                try:
                    output = next(outputs)
                except StopIteration:
                    break
                self.send(_resolve(input_bag, output))

    def finalize(self):
        # pylint: disable=broad-except
        assert self.state is RUNNING, ('A {} must be in {} state at finalization time.').format(
            type(self).__name__, RUNNING)
        self.state = TERMINATED

        super().finalize()


def _iter(mixed):
    if isinstance(mixed, (dict, list, str)):
        raise TypeError(type(mixed).__name__)
    return iter(mixed)


def _resolve(input_bag, output):
    # NotModified means to send the input unmodified to output.
    if output is NOT_MODIFIED:
        return input_bag

    # If it does not look like a bag, let's create one for easier manipulation
    if hasattr(output, 'apply'):
        # Already a bag? Check if we need to set parent.
        if INHERIT_INPUT in output.flags:
            output.set_parent(input_bag)
    else:
        # Not a bag? Let's encapsulate it.
        output = Bag(output)

    return output
