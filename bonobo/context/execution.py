import traceback
import sys
from functools import partial
from queue import Empty
from time import sleep

from bonobo.constants import BEGIN, END, NOT_MODIFIED, INHERIT_INPUT
from bonobo.context.processors import get_context_processors
from bonobo.core.inputs import Input
from bonobo.core.statistics import WithStatistics
from bonobo.errors import InactiveReadableError
from bonobo.structs.bags import Bag, ErrorBag
from bonobo.util.objects import Wrapper


class GraphExecutionContext:
    @property
    def started(self):
        return any(node.started for node in self.nodes)

    @property
    def stopped(self):
        return all(node.started and node.stopped for node in self.nodes)

    @property
    def alive(self):
        return any(node.alive for node in self.nodes)

    def __init__(self, graph, plugins=None):
        self.graph = graph
        self.nodes = [NodeExecutionContext(node, parent=self) for node in self.graph.nodes]
        self.plugins = [PluginExecutionContext(plugin, parent=self) for plugin in plugins or ()]

        for i, component_context in enumerate(self):
            try:
                component_context.outputs = [self[j].input for j in self.graph.outputs_of(i)]
            except KeyError:
                continue

            component_context.input.on_begin = partial(component_context.send, BEGIN, _control=True)
            component_context.input.on_end = partial(component_context.send, END, _control=True)
            component_context.input.on_finalize = partial(component_context.stop)

    def __getitem__(self, item):
        return self.nodes[item]

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        yield from self.nodes

    def recv(self, *messages):
        """Push a list of messages in the inputs of this graph's inputs, matching the output of special node "BEGIN" in
        our graph."""

        for i in self.graph.outputs_of(BEGIN):
            for message in messages:
                self[i].recv(message)

    def start(self):
        # todo use strategy
        for node in self.nodes:
            node.start()

    def loop(self):
        # todo use strategy
        for node in self.nodes:
            node.loop()

    def stop(self):
        # todo use strategy
        for node in self.nodes:
            node.stop()


def ensure_tuple(tuple_or_mixed):
    if isinstance(tuple_or_mixed, tuple):
        return tuple_or_mixed
    return (tuple_or_mixed, )


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

    def __init__(self, wrapped, parent):
        super().__init__(wrapped)
        self.parent = parent
        self._started, self._stopped, self._context, self._stack = False, False, None, []

    def start(self):
        assert self.state == (False,
                              False), ('{}.start() can only be called on a new node.').format(type(self).__name__)
        assert self._context is None

        self._started = True
        self._context = ()
        for processor in get_context_processors(self.wrapped):
            _processed = processor(self.wrapped, self, *self._context)
            try:
                # todo yield from ?
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
        """
        TODO xxx this is a step, not a loop
        """
        raise NotImplementedError('Abstract.')

    def stop(self):
        assert self._started, ('{}.stop() can only be called on a previously started node.').format(type(self).__name__)
        if self._stopped:
            return

        assert self._context is not None

        self._stopped = True
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
        """
        Error handler. Whatever happens in a plugin or component, if it looks like an exception, taste like an exception
        or somehow make me think it is an exception, I'll handle it.

        :param exc: the culprit
        :param trace: Hercule Poirot's logbook.
        :return: to hell
        """

        from colorama import Fore, Style
        print(
            Style.BRIGHT,
            Fore.RED,
            '\U0001F4A3 {} in {}'.format(type(exc).__name__, self.wrapped),
            Style.RESET_ALL,
            sep='',
            file=sys.stderr,
        )
        print(trace)


class PluginExecutionContext(LoopingExecutionContext):
    PERIOD = 0.5

    def __init__(self, wrapped, parent):
        # Instanciate plugin. This is not yet considered stable, as at some point we may need a way to configure
        # plugins, for example if it depends on an external service.
        super().__init__(wrapped(self), parent)

    def start(self):
        super().start()

        try:
            self.wrapped.initialize()
        except Exception as exc:  # pylint: disable=broad-except
            self.handle_error(exc, traceback.format_exc())

    def shutdown(self):
        try:
            self.wrapped.finalize()
        except Exception as exc:  # pylint: disable=broad-except
            self.handle_error(exc, traceback.format_exc())
        finally:
            self.alive = False

    def step(self):
        try:
            self.wrapped.run()
        except Exception as exc:  # pylint: disable=broad-except
            self.handle_error(exc, traceback.format_exc())


class NodeExecutionContext(WithStatistics, LoopingExecutionContext):
    """
    todo: make the counter dependant of parent context?
    """

    @property
    def alive(self):
        """todo check if this is right, and where it is used"""
        return self.input.alive and self._started and not self._stopped

    def __init__(self, wrapped, parent):
        LoopingExecutionContext.__init__(self, wrapped, parent)
        WithStatistics.__init__(self, 'in', 'out', 'err')

        self.input = Input()
        self.outputs = []

    def __str__(self):
        return (('+' if self.alive else '-') + ' ' + self.__name__ + ' ' + self.get_statistics_as_string()).strip()

    def __repr__(self):
        return '<' + self.__str__() + '>'

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

    def handle_results(self, input_bag, results):
        # self._exec_time += timer.duration
        # Put data onto output channels
        try:
            results = _iter(results)
        except TypeError:  # not an iterator
            if results:
                if isinstance(results, ErrorBag):
                    results.apply(self.handle_error)
                else:
                    self.send(_resolve(input_bag, results))
            else:
                # case with no result, an execution went through anyway, use for stats.
                # self._exec_count += 1
                pass
        else:
            while True:  # iterator
                try:
                    output = next(results)
                except StopIteration:
                    break
                else:
                    if isinstance(output, ErrorBag):
                        output.apply(self.handle_error)
                    else:
                        self.send(_resolve(input_bag, output))


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
