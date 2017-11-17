import itertools

from bonobo.constants import INHERIT_INPUT, LOOPBACK
from bonobo.structs.tokens import Token

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

    default_flags = ()

    @staticmethod
    def format_args(*args, **kwargs):
        return ', '.join(itertools.chain(map(repr, args), ('{}={!r}'.format(k, v) for k, v in kwargs.items())))

    def __new__(cls, *args, _flags=None, _parent=None, **kwargs):
        # Handle the special case where we call Bag's constructor with only one bag or token as argument.
        if len(args) == 1 and len(kwargs) == 0:
            if isinstance(args[0], Bag):
                raise ValueError('Bag cannot be instanciated with a bag (for now ...).')

            if isinstance(args[0], Token):
                return args[0]

        # Otherwise, type will handle that for us.
        return super().__new__(cls)

    def __init__(self, *args, _flags=None, _parent=None, _argnames=None, **kwargs):
        self._flags = type(self).default_flags + (_flags or ())
        self._argnames = _argnames
        self._parent = _parent

        if len(args) == 1 and len(kwargs) == 0:
            # If we only have one argument, that may be because we're using the shorthand syntax.
            mixed = args[0]

            if isinstance(mixed, Bag):
                # Just duplicate the bag.
                self._args = mixed.args
                self._kwargs = mixed.kwargs
            elif isinstance(mixed, tuple):
                if not len(mixed):
                    # Empty bag.
                    self._args = ()
                    self._kwargs = {}
                elif isinstance(mixed[-1], dict):
                    # Args + Kwargs
                    self._args = mixed[:-1]
                    self._kwargs = mixed[-1]
                else:
                    # Args only
                    self._args = mixed
                    self._kwargs = {}
            elif isinstance(mixed, dict):
                # Kwargs only
                self._args = ()
                self._kwargs = mixed
            else:
                self._args = args
                self._kwargs = {}

        else:
            # Otherwise, lets get args/kwargs from the constructor.
            self._args = args
            self._kwargs = kwargs

    def __repr__(self):
        return 'Bag({})'.format(Bag.format_args(*self.args, **self.kwargs))

    @property
    def args(self):
        if self._parent is None:
            return self._args
        return (
            *self._parent.args,
            *self._args,
        )

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

    @property
    def specials(self):
        return {k: self.__dict__[k] for k in ('_argnames', ) if k in self.__dict__ and self.__dict__[k]}

    def apply(self, func_or_iter, *args, **kwargs):
        if callable(func_or_iter):
            return func_or_iter(*args, *self.args, **kwargs, **self.kwargs, **self.specials)

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
        # XXX there are overlapping cases, but this is very handy for now. Let's think about it later.

        # bag
        if isinstance(other, Bag) and other.args == self.args and other.kwargs == self.kwargs:
            return True

        # tuple
        if isinstance(other, tuple):
            # self == ()
            if not len(other):
                return not self.args and not self.kwargs

            if isinstance(other[-1], dict):
                # self == (*args, {**kwargs}) ?
                return other[:-1] == self.args and other[-1] == self.kwargs

            # self == (*args) ?
            return other == self.args and not self.kwargs

        # dict (aka kwargs)
        if isinstance(other, dict) and not self.args and other == self.kwargs:
            return True

        return len(self.args) == 1 and not self.kwargs and self.args[0] == other

    def args_as_dict(self):
        return dict(zip(self._argnames, self.args))


class LoopbackBag(Bag):
    default_flags = (LOOPBACK, )


class ErrorBag(Bag):
    pass
