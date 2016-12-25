from operator import attrgetter

import itertools

from bonobo.util.tokens import Token

_get_args = attrgetter('args')

InheritInputFlag = Token('InheritInputFlag')


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
        return (
            *self._parent.args,
            *self._args, )

    @property
    def kwargs(self):
        if self._parent is None:
            return self._kwargs
        return {
            ** self._parent.kwargs,
            ** self._kwargs,
        }

    @property
    def flags(self):
        return self._flags

    def apply(self, f, *args, **kwargs):
        return f(*args, *self.args, **kwargs, **self.kwargs)

    def extend(self, *args, **kwargs):
        return type(self)(*args, _parent=self, **kwargs)

    def set_parent(self, parent):
        self._parent = parent

    @classmethod
    def inherit(cls, *args, **kwargs):
        return cls(*args, _flags=(InheritInputFlag, ), **kwargs)

    def __repr__(self):
        return '<{} ({})>'.format(
            type(self).__name__, ', '.join(
                itertools.chain(
                    map(repr, self.args),
                    ('{}={}'.format(k, repr(v)) for k, v in self.kwargs.items()), )))
