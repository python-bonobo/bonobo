import functools
import warnings
from functools import partial

from bonobo import Bag
from bonobo.config import Configurable, Method

_isarg = lambda item: type(item) is int
_iskwarg = lambda item: type(item) is str


class Operation():
    def __init__(self, item, callable):
        self.item = item
        self.callable = callable

    def __repr__(self):
        return '<operation {} on {}>'.format(self.callable.__name__, self.item)

    def apply(self, *args, **kwargs):
        if _isarg(self.item):
            return (*args[0:self.item], self.callable(args[self.item]), *args[self.item + 1:]), kwargs
        if _iskwarg(self.item):
            return args, {**kwargs, self.item: self.callable(kwargs.get(self.item))}
        raise RuntimeError('Houston, we have a problem...')


class FactoryOperation():
    def __init__(self, factory, callable):
        self.factory = factory
        self.callable = callable

    def __repr__(self):
        return '<factory operation {}>'.format(self.callable.__name__)

    def apply(self, *args, **kwargs):
        return self.callable(*args, **kwargs)


CURSOR_TYPES = {}


def operation(mixed):
    def decorator(m, ctype=mixed):
        def lazy_operation(self, *args, **kwargs):
            @functools.wraps(m)
            def actual_operation(x):
                return m(self, x, *args, **kwargs)

            self.factory.operations.append(Operation(self.item, actual_operation))
            return CURSOR_TYPES[ctype](self.factory, self.item) if ctype else self

        return lazy_operation

    return decorator if isinstance(mixed, str) else decorator(mixed, ctype=None)


def factory_operation(m):
    def lazy_operation(self, *config):
        @functools.wraps(m)
        def actual_operation(*args, **kwargs):
            return m(self, *config, *args, **kwargs)

        self.operations.append(FactoryOperation(self, actual_operation))
        return self

    return lazy_operation


class Cursor():
    _type = None

    def __init__(self, factory, item):
        self.factory = factory
        self.item = item

    @operation('dict')
    def as_dict(self, x):
        return x if isinstance(x, dict) else dict(x)

    @operation('int')
    def as_int(self, x):
        return x if isinstance(x, int) else int(x)

    @operation('str')
    def as_str(self, x):
        return x if isinstance(x, str) else str(x)

    @operation('list')
    def as_list(self, x):
        return x if isinstance(x, list) else list(x)

    @operation('tuple')
    def as_tuple(self, x):
        return x if isinstance(x, tuple) else tuple(x)

    def __getattr__(self, item):
        """
        Fallback to type methods if they exist, for example StrCursor.upper will use str.upper if not overriden, etc.

        :param item:
        """
        if self._type and item in self._type.__dict__:
            method = self._type.__dict__[item]

            @operation
            @functools.wraps(method)
            def _operation(self, x, *args, **kwargs):
                return method(x, *args, **kwargs)

            setattr(self, item, partial(_operation, self))
            return getattr(self, item)

        raise AttributeError('Unknown operation {}.{}().'.format(
            type(self).__name__,
            item,
        ))


CURSOR_TYPES['default'] = Cursor


class DictCursor(Cursor):
    _type = dict

    @operation('default')
    def get(self, x, path):
        return x.get(path)

    @operation
    def map_keys(self, x, mapping):
        return {mapping.get(k): v for k, v in x.items()}


CURSOR_TYPES['dict'] = DictCursor


class StringCursor(Cursor):
    _type = str


CURSOR_TYPES['str'] = StringCursor


class Factory(Configurable):
    initialize = Method(required=False)

    def __init__(self, *args, **kwargs):
        warnings.warn(
            type(self).__name__ +
            ' is experimental, API may change in the future, use it as a preview only and knowing the risks.',
            FutureWarning
        )
        super(Factory, self).__init__(*args, **kwargs)
        self.default_cursor_type = 'default'
        self.operations = []

        if self.initialize is not None:
            self.initialize(self)

    @factory_operation
    def move(self, _from, _to, *args, **kwargs):
        if _from == _to:
            return args, kwargs

        if _isarg(_from):
            value = args[_from]
            args = args[:_from] + args[_from + 1:]
        elif _iskwarg(_from):
            value = kwargs[_from]
            kwargs = {k: v for k, v in kwargs if k != _from}
        else:
            raise RuntimeError('Houston, we have a problem...')

        if _isarg(_to):
            return (*args[:_to], value, *args[_to + 1:]), kwargs
        elif _iskwarg(_to):
            return args, {**kwargs, _to: value}
        else:
            raise RuntimeError('Houston, we have a problem...')

    def __call__(self, *args, **kwargs):
        for operation in self.operations:
            args, kwargs = operation.apply(*args, **kwargs)
        return Bag(*args, **kwargs)

    def __getitem__(self, item):
        return CURSOR_TYPES[self.default_cursor_type](self, item)
