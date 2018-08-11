from collections import Iterable
from contextlib import contextmanager
from functools import partial
from inspect import signature

from bonobo.config import Option
from bonobo.errors import UnrecoverableTypeError
from bonobo.util import deprecated_alias, ensure_tuple

_raw = object()
_args = object()
_none = object()

INPUT_FORMATS = {_raw, _args, _none}


class ContextProcessor(Option):
    """
    A ContextProcessor is a kind of transformation decorator that can setup and teardown a transformation and runtime
    related dependencies, at the execution level.

    It works like a yielding context manager, and is the recommended way to setup and teardown objects you'll need
    in the context of one execution. It's the way to overcome the stateless nature of transformations.

    The yielded values will be passed as positional arguments to the next context processors (order does matter), and
    finally to the __call__ method of the transformation.

    Warning: this may change for a similar but simpler implementation, don't rely too much on it (yet).

    Example:

        >>> from bonobo.config import Configurable
        >>> from bonobo.util import ValueHolder

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


class bound(partial):
    @property
    def kwargs(self):
        return self.keywords


class ContextCurrifier:
    """
    This is a helper to resolve processors.
    """

    def __init__(self, wrapped, *args, **kwargs):
        self.wrapped = wrapped
        self.args = args
        self.kwargs = kwargs
        self.format = getattr(wrapped, '__input_format__', _args)
        self._stack, self._stack_values = None, None

    def __iter__(self):
        yield from self.wrapped

    def _bind(self, _input):
        try:
            bind = signature(self.wrapped).bind
        except ValueError:
            bind = partial(bound, self.wrapped)
        if self.format is _args:
            return bind(*self.args, *_input, **self.kwargs)
        if self.format is _raw:
            return bind(*self.args, _input, **self.kwargs)
        if self.format is _none:
            return bind(*self.args, **self.kwargs)
        raise NotImplementedError('Invalid format {!r}.'.format(self.format))

    def __call__(self, _input):
        if not callable(self.wrapped):
            if isinstance(self.wrapped, Iterable):
                return self.__iter__()
            raise UnrecoverableTypeError('Uncallable node {}'.format(self.wrapped))
        try:
            bound = self._bind(_input)
        except TypeError as exc:
            raise UnrecoverableTypeError(
                (
                    'Input of {wrapped!r} does not bind to the node signature.\n'
                    'Args: {args}\n'
                    'Input: {input}\n'
                    'Kwargs: {kwargs}\n'
                    'Signature: {sig}'
                ).format(
                    wrapped=self.wrapped, args=self.args, input=_input, kwargs=self.kwargs, sig=signature(self.wrapped)
                )
            ) from exc
        return self.wrapped(*bound.args, **bound.kwargs)

    def setup(self, *context):
        if self._stack is not None:
            raise RuntimeError('Cannot setup context currification twice.')

        self._stack, self._stack_values = list(), list()
        for processor in resolve_processors(self.wrapped):
            _processed = processor(self.wrapped, *context, *self.args, **self.kwargs)
            _append_to_context = next(_processed)
            self._stack_values.append(_append_to_context)
            if _append_to_context is not None:
                self.args += ensure_tuple(_append_to_context)
            self._stack.append(_processed)

    def teardown(self):
        while self._stack:
            processor = self._stack.pop()
            try:
                # todo yield from ? how to ?
                processor.send(self._stack_values.pop())
            except StopIteration:
                # This is normal, and wanted.
                pass
            else:
                # No error ? We should have had StopIteration ...
                raise RuntimeError('Context processors should not yield more than once.')
        self._stack, self._stack_values = None, None

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


def use_context(f):
    def context(self, context, *args, **kwargs):
        yield context

    return use_context_processor(context)(f)


def use_context_processor(context_processor):
    def using_context_processor(cls_or_func):
        nonlocal context_processor

        try:
            cls_or_func.__processors__
        except AttributeError:
            cls_or_func.__processors__ = []

        cls_or_func.__processors__.append(ContextProcessor(context_processor))
        return cls_or_func

    return using_context_processor


def _use_input_format(input_format):
    if input_format not in INPUT_FORMATS:
        raise ValueError(
            'Invalid input format {!r}. Choices: {}'.format(input_format, ', '.join(sorted(INPUT_FORMATS)))
        )

    def _set_input_format(f):
        setattr(f, '__input_format__', input_format)
        return f

    return _set_input_format


use_no_input = _use_input_format(_none)
use_raw_input = _use_input_format(_raw)
