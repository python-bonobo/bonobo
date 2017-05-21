import functools
from functools import partial


def get_name(mixed):
    try:
        return mixed.__name__
    except AttributeError:
        return type(mixed).__name__


class Wrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    @property
    def __name__(self):
        return getattr(self.wrapped, '__name__', getattr(type(self.wrapped), '__name__', repr(self.wrapped)))

    name = __name__


class ValueHolder:
    """
    Decorator holding a value in a given memory adress, effectively allowing to "hold" even an immutable typed value as the state of a
    node, allowing different actors to mutate it durably.

    For the sake of concistency, all operator methods have been implemented (see https://docs.python.org/3/reference/datamodel.html) or
    at least all in a certain category, but it feels like a more correct method should exist, like with a getattr-something on the
    value. Let's see later.
    
    """

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        # XXX deprecated
        return self._value

    def get(self):
        return self._value

    def set(self, new_value):
        self._value = new_value

    def __bool__(self):
        return bool(self._value)

    def __eq__(self, other):
        return self._value == other

    def __ne__(self, other):
        return self._value != other

    def __repr__(self):
        return repr(self._value)

    def __lt__(self, other):
        return self._value < other

    def __le__(self, other):
        return self._value <= other

    def __gt__(self, other):
        return self._value > other

    def __ge__(self, other):
        return self._value >= other

    def __add__(self, other):
        return self._value + other

    def __radd__(self, other):
        return other + self._value

    def __iadd__(self, other):
        self._value += other
        return self

    def __sub__(self, other):
        return self._value - other

    def __rsub__(self, other):
        return other - self._value

    def __isub__(self, other):
        self._value -= other
        return self

    def __mul__(self, other):
        return self._value * other

    def __rmul__(self, other):
        return other * self._value

    def __imul__(self, other):
        self._value *= other
        return self

    def __matmul__(self, other):
        return self._value @ other

    def __rmatmul__(self, other):
        return other @ self._value

    def __imatmul__(self, other):
        self._value @= other
        return self

    def __truediv__(self, other):
        return self._value / other

    def __rtruediv__(self, other):
        return other / self._value

    def __itruediv__(self, other):
        self._value /= other
        return self

    def __floordiv__(self, other):
        return self._value // other

    def __rfloordiv__(self, other):
        return other // self._value

    def __ifloordiv__(self, other):
        self._value //= other
        return self

    def __mod__(self, other):
        return self._value % other

    def __rmod__(self, other):
        return other % self._value

    def __imod__(self, other):
        self._value %= other
        return self

    def __divmod__(self, other):
        return divmod(self._value, other)

    def __rdivmod__(self, other):
        return divmod(other, self._value)

    def __pow__(self, other):
        return self._value**other

    def __rpow__(self, other):
        return other**self._value

    def __ipow__(self, other):
        self._value **= other
        return self

    def __lshift__(self, other):
        return self._value << other

    def __rlshift__(self, other):
        return other << self._value

    def __ilshift__(self, other):
        self._value <<= other
        return self

    def __rshift__(self, other):
        return self._value >> other

    def __rrshift__(self, other):
        return other >> self._value

    def __irshift__(self, other):
        self._value >>= other
        return self

    def __and__(self, other):
        return self._value & other

    def __rand__(self, other):
        return other & self._value

    def __iand__(self, other):
        self._value &= other
        return self

    def __xor__(self, other):
        return self._value ^ other

    def __rxor__(self, other):
        return other ^ self._value

    def __ixor__(self, other):
        self._value ^= other
        return self

    def __or__(self, other):
        return self._value | other

    def __ror__(self, other):
        return other | self._value

    def __ior__(self, other):
        self._value |= other
        return self

    def __neg__(self):
        return -self._value

    def __pos__(self):
        return +self._value

    def __abs__(self):
        return abs(self._value)

    def __invert__(self):
        return ~self._value

    def __len__(self):
        return len(self._value)


def get_attribute_or_create(obj, attr, default):
    try:
        return getattr(obj, attr)
    except AttributeError:
        setattr(obj, attr, default)
        return getattr(obj, attr)
