import itertools

from bonobo.constants import INHERIT_INPUT

__all__ = [
    'Bag',
    'ErrorBag',
]


class Bag:
    """
    Bags are simple datastructures that holds arguments and keyword arguments together, that may be applied to a
    callable.
    
    Example:
    
        >>> from bonobo import Bag
        >>> def myfunc(foo, *, bar):
        ...     print(foo, bar)
        ...
        >>> bag = Bag('foo', bar='baz')
        >>> bag.apply(myfunc)
        foo baz
    
    A bag can inherit another bag, allowing to override only a few arguments without touching the parent.
    
    Example:
        
        >>> bag2 = Bag(bar='notbaz', _parent=bag)
        >>> bag2.apply(myfunc)
        foo notbaz
    
    """

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
                    yield from func_or_iter

                return generator()
            except TypeError as exc:
                raise TypeError('Could not apply bag to {}.'.format(func_or_iter)) from exc

        raise TypeError('Could not apply bag to {}.'.format(func_or_iter))

    def get(self):
        """
        Get a 2 element tuple of this bag's args and kwargs.

        :return: tuple
        """
        return self.args, self.kwargs

    def extend(self, *args, **kwargs):
        return type(self)(*args, _parent=self, **kwargs)

    def set_parent(self, parent):
        self._parent = parent

    @classmethod
    def inherit(cls, *args, **kwargs):
        return cls(*args, _flags=(INHERIT_INPUT, ), **kwargs)

    def __eq__(self, other):
        return isinstance(other, Bag) and other.args == self.args and other.kwargs == self.kwargs

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
