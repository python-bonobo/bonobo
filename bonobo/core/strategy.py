import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty

from bonobo.core.errors import InactiveReadableError
from bonobo.core.io import Input
from bonobo.core.tokens import BEGIN, Token
from bonobo.util.iterators import force_iterator, IntegerSequenceGenerator

NEW = Token('New')
RUNNING = Token('Running')
TERMINATED = Token('Terminated')


def noop(*args, **kwargs): pass


def get_initializer(c):
    return getattr(c, 'initialize', noop)


def get_finalizer(c):
    return getattr(c, 'finalize', noop)


class ComponentExecutionContext:
    """
    todo: make the counter dependant of parent context?
    """

    # todo clean this xxx
    __thread_counter = IntegerSequenceGenerator()

    @property
    def name(self):
        return self.component.__name__ + '-' + str(self.__thread_number)

    def __init__(self, component):
        # todo clean this xxx
        self.__thread_number = next(self.__class__.__thread_counter)

        self.component = component
        self.input = Input()
        self.outputs = []

        self.state = NEW

    def __repr__(self):
        """Adds "alive" information to the transform representation."""
        return ('+' if self.running else '-') + ' ' + self.name + ' ' + self.component.get_stats_as_string()

    def step(self, finalize=False):
        # Pull data from the first available input channel.
        row = self.input.get(timeout=1)

        self.__execute_and_handle_output(self.component, row)

    def run(self):
        assert self.state is NEW, ('A {} can only be run once, and thus is expected to be in {} state at the '
                                   'beginning of a run().').format(type(self).__name__, NEW)

        self.state = RUNNING
        get_initializer(self.component)(self)

        while True:
            try:
                self.step()
            except KeyboardInterrupt as e:
                raise
            except InactiveReadableError as e:
                # Terminated, exit loop.
                break
            except Empty as e:
                continue
            except Exception as e:
                self.handle_error(e, traceback.format_exc())

        assert self.state is RUNNING, ('A {} must be in {} state when finalization starts.').format(
            type(self).__name__, RUNNING)

        try:
            self.state = TERMINATED
            get_finalizer(self.component)(self)
        except Exception as e:
            self.handle_error(e, traceback.format_exc())

    def handle_error(self, exc, tb):
        raise NotImplementedError()
        if STDERR in self.transform.OUTPUT_CHANNELS:
            self.transform._output.put(({
                                            'transform': self.transform,
                                            'exception': exc,
                                            'traceback': tb,
                                        }, STDERR,))
            print((str(exc) + '\n\n' + tb + '\n\n\n\n'))
        else:
            print((str(exc) + '\n\n' + tb + '\n\n\n\n'))

    # Private
    def __execute_and_handle_output(self, callable, *args, **kwargs):
        """Runs a transformation callable with given args/kwargs and flush the result into the right
        output channel."""

        timer = Timer()
        with timer:
            results = callable(*args, **kwargs)
        self._exec_time += timer.duration

        # Put data onto output channels
        if isinstance(results, types.GeneratorType):
            while True:
                timer = Timer()
                with timer:
                    try:
                        result = next(results)
                    except StopIteration as e:
                        break
                self._exec_time += timer.duration
                self._exec_count += 1
                self._output.put(result)
        elif results is not None:
            self._exec_count += 1
            self._output.put(results)
        else:
            self._exec_count += 1


class ExecutionContext:
    def __init__(self, graph):
        self.graph = graph


class Strategy:
    context_type = ExecutionContext

    def create_context(self, graph, *args, **kwargs):
        return self.context_type(graph)

    def execute(self, graph, *args, **kwargs):
        raise NotImplementedError


class NaiveStrategy(Strategy):
    def execute(self, graph, *args, **kwargs):
        context = self.create_context(graph)

        input_queues = {i: Queue() for i in range(len(context.graph.components))}
        for i, component in enumerate(context.graph.components):
            while True:
                try:
                    args = (input_queues[i].get(block=False),) if i else ()
                    for row in force_iterator(component(*args)):
                        input_queues[i + 1].put(row)
                    if not i:
                        raise Empty
                except Empty:
                    break


class ExecutorStrategy(Strategy):
    executor_type = ThreadPoolExecutor

    def __init__(self, executor=None):
        self.executor = executor or self.executor_type()

    def execute(self, graph, *args, **kwargs):
        context = self.create_context(graph)

        for i in graph.outputs_of(BEGIN):
            self.call_component(i, *args, **kwargs)

        raise NotImplementedError()

        while len(self.running):
            # print(self.running)
            time.sleep(0.1)

        f = self.executor.submit(self.components[idx], *args, **kwargs)
        self.running.add(f)

        idx = i

        @f.add_done_callback
        def on_component_done(f):
            nonlocal self, idx

            outputs = self.outputs_of(idx)
            results = force_iterator(f.result())

            if results:
                for result in results:
                    for output in outputs:
                        self.call_component(output, result)

            self.running.remove(f)

    def __run_component(self, component):
        c_in = Input()

        while c_in.alive:
            row = c_in.get()
            component(row)
