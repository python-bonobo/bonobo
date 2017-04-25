import itertools

from bonobo.constants import INHERIT_INPUT

__all__ = [
    'Bag',
    'ErrorBag',
]


class Bag:
    def __init__(self, *args, _flags=None, _parent=None, **kwargs):
        self._flags = _flags or ()
        self._parent = _parent
        self._args = args
        self._kwargs = kwargs

    @property
    def args(self):
        if self._parent is None:
            return self._args
        return (*self._parent.args, *self._args, )

    @property
    def kwargs(self):
        if self._parent is None:
            return self._kwargs
        return {
            **self._parent.kwargs,
            **self._kwargs,
        }

    @property
    def flags(self):
        return self._flags

    def apply(self, func_or_iter, *args, **kwargs):
        if callable(func_or_iter):
            return func_or_iter(*args, *self.args, **kwargs, **self.kwargs)

        if len(args) == 0 and len(kwargs) == 0:
            try:
                iter(func_or_iter)

                def generator():
                    nonlocal func_or_iter
                    for x in func_or_iter:
                        yield x

                return generator()
            except TypeError as exc:
                raise TypeError('Could not apply bag to {}.'.format(func_or_iter)) from exc

        raise TypeError('Could not apply bag to {}.'.format(func_or_iter))

    def extend(self, *args, **kwargs):
        return type(self)(*args, _parent=self, **kwargs)

    def set_parent(self, parent):
        self._parent = parent

    @classmethod
    def inherit(cls, *args, **kwargs):
        return cls(*args, _flags=(INHERIT_INPUT, ), **kwargs)

    def __repr__(self):
        return '<{} ({})>'.format(
            type(self).__name__, ', '.
            join(itertools.chain(
                map(repr, self.args),
                ('{}={}'.format(k, repr(v)) for k, v in self.kwargs.items()),
            ))
        )


class ErrorBag(Bag):
    pass
