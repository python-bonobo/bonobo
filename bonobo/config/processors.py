import functools

import types

from bonobo.util.compat import deprecated_alias, deprecated

from bonobo.config.options import Option
from bonobo.util.iterators import ensure_tuple

_CONTEXT_PROCESSORS_ATTR = '__processors__'


class ContextProcessor(Option):
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

    def __call__(self, *args, **kwargs):
        return self.wrapped(*self.context, *args, **kwargs)

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


@deprecated
def add_context_processor(cls_or_func, context_processor):
    getattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR).append(context_processor)


@deprecated
def contextual(cls_or_func):
    """
    Make sure an element has the context processors collection.
    
    :param cls_or_func: 
    """
    if not add_context_processor.__name__ in cls_or_func.__dict__:
        setattr(cls_or_func, add_context_processor.__name__, functools.partial(add_context_processor, cls_or_func))

    if isinstance(cls_or_func, types.FunctionType):
        try:
            getattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR)
        except AttributeError:
            setattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR, [])
        return cls_or_func

    if not _CONTEXT_PROCESSORS_ATTR in cls_or_func.__dict__:
        setattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR, [])

    _processors = getattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR)
    for processor in cls_or_func.__dict__.values():
        if isinstance(processor, ContextProcessor):
            _processors.append(processor)

    # This is needed for python 3.5, python 3.6 should be fine, but it's considered an implementation detail.
    _processors.sort(key=lambda proc: proc._creation_counter)
    return cls_or_func


def resolve_processors(mixed):
    try:
        yield from mixed.__processors__
    except AttributeError:
        # old code, deprecated usage
        if isinstance(mixed, types.FunctionType):
            yield from getattr(mixed, _CONTEXT_PROCESSORS_ATTR, ())

        for cls in reversed((mixed if isinstance(mixed, type) else type(mixed)).__mro__):
            yield from cls.__dict__.get(_CONTEXT_PROCESSORS_ATTR, ())

    return ()


get_context_processors = deprecated_alias('get_context_processors', resolve_processors)
