from collections import Iterable
from contextlib import contextmanager

from bonobo.config.options import Option
from bonobo.util.compat import deprecated_alias
from bonobo.util.iterators import ensure_tuple

_CONTEXT_PROCESSORS_ATTR = '__processors__'


class ContextProcessor(Option):
    """
    A ContextProcessor is a kind of transformation decorator that can setup and teardown a transformation and runtime
    related dependencies, at the execution level.

    It works like a yielding context manager, and is the recommended way to setup and teardown objects you'll need
    in the context of one execution. It's the way to overcome the stateless nature of transformations.

    The yielded values will be passed as positional arguments to the next context processors (order do matter), and
    finally to the __call__ method of the transformation.

    Warning: this may change for a similar but simpler implementation, don't relly too much on it (yet).

    Example:

        >>> from bonobo.config import Configurable
        >>> from bonobo.util.objects import ValueHolder

        >>> class Counter(Configurable):
        ...     @ContextProcessor
        ...     def counter(self, context):
        ...         yield ValueHolder(0)
        ...
        ...     def __call__(self, counter, *args, **kwargs):
        ...         counter += 1
        ...         yield counter.get()

    """

    @property
    def __name__(self):
        return self.func.__name__

    def __init__(self, func):
        self.func = func
        super(ContextProcessor, self).__init__(required=False, default=self.__name__)
        self.name = self.__name__

    def __repr__(self):
        return repr(self.func).replace('<function', '<{}'.format(type(self).__name__))

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @classmethod
    def decorate(cls, cls_or_func):
        try:
            cls_or_func.__processors__
        except AttributeError:
            cls_or_func.__processors__ = []

        def decorator(processor, cls_or_func=cls_or_func):
            cls_or_func.__processors__.append(cls(processor))
            return cls_or_func

        return decorator


class ContextCurrifier:
    """
    This is a helper to resolve processors.
    """

    def __init__(self, wrapped, *initial_context):
        self.wrapped = wrapped
        self.context = tuple(initial_context)
        self._stack = []
        self._stack_values = []

    def __iter__(self):
        yield from self.wrapped

    def __call__(self, *args, **kwargs):
        if not callable(self.wrapped) and isinstance(self.wrapped, Iterable):
            return self.__iter__()
        return self.wrapped(*self.context, *args, **kwargs)

    def setup(self, *context):
        if len(self._stack):
            raise RuntimeError('Cannot setup context currification twice.')
        for processor in resolve_processors(self.wrapped):
            _processed = processor(self.wrapped, *context, *self.context)
            _append_to_context = next(_processed)
            self._stack_values.append(_append_to_context)
            if _append_to_context is not None:
                self.context += ensure_tuple(_append_to_context)
            self._stack.append(_processed)

    def teardown(self):
        while len(self._stack):
            processor = self._stack.pop()
            try:
                # todo yield from ? how to ?
                processor.send(self._stack_values.pop())
            except StopIteration as exc:
                # This is normal, and wanted.
                pass
            else:
                # No error ? We should have had StopIteration ...
                raise RuntimeError('Context processors should not yield more than once.')

    @contextmanager
    def as_contextmanager(self, *context):
        """
        Convenience method to use it as a contextmanager, mostly for test purposes.

        Example:

            >>> with ContextCurrifier(node).as_contextmanager(context) as stack:
            ...     stack()

        :param context:
        :return:
        """
        self.setup(*context)
        yield self
        self.teardown()


def resolve_processors(mixed):
    try:
        yield from mixed.__processors__
    except AttributeError:
        yield from ()


get_context_processors = deprecated_alias('get_context_processors', resolve_processors)
