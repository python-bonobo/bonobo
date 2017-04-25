from functools import partial

import types

_CONTEXT_PROCESSORS_ATTR = '__processors__'


def get_context_processors(mixed):
    if isinstance(mixed, types.FunctionType):
        yield from getattr(mixed, _CONTEXT_PROCESSORS_ATTR, ())

    for cls in reversed((mixed if isinstance(mixed, type) else type(mixed)).__mro__):
        yield from cls.__dict__.get(_CONTEXT_PROCESSORS_ATTR, ())

    return ()


class ContextProcessor:
    _creation_counter = 0

    @property
    def __name__(self):
        return self.func.__name__

    def __init__(self, func):
        self.func = func

        # This hack is necessary for python3.5
        self._creation_counter = ContextProcessor._creation_counter
        ContextProcessor._creation_counter += 1

    def __repr__(self):
        return repr(self.func).replace('<function', '<{}'.format(type(self).__name__))

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def add_context_processor(cls_or_func, context_processor):
    getattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR).append(context_processor)


def contextual(cls_or_func):
    """
    Make sure an element has the context processors collection.
    
    :param cls_or_func: 
    """
    if not add_context_processor.__name__ in cls_or_func.__dict__:
        setattr(cls_or_func, add_context_processor.__name__, partial(add_context_processor, cls_or_func))

    if isinstance(cls_or_func, types.FunctionType):
        try:
            getattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR)
        except AttributeError:
            setattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR, [])
        return cls_or_func

    if not _CONTEXT_PROCESSORS_ATTR in cls_or_func.__dict__:
        setattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR, [])

    _processors = getattr(cls_or_func, _CONTEXT_PROCESSORS_ATTR)
    for name, value in cls_or_func.__dict__.items():
        if isinstance(value, ContextProcessor):
            _processors.append(value)
    # This is needed for python 3.5, python 3.6 should be fine, but it's considered an implementation detail.
    _processors.sort(key=lambda proc: proc._creation_counter)
    return cls_or_func
