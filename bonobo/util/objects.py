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

    def __init__(self, value, *, type=None):
        self.value = value
        self.type = type

    def __repr__(self):
        return repr(self.value)

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return other + self.value

    def __iadd__(self, other):
        self.value += other
        return self

    def __sub__(self, other):
        return self.value - other

    def __rsub__(self, other):
        return other - self.value

    def __isub__(self, other):
        self.value -= other
        return self

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __imul__(self, other):
        self.value *= other
        return self

    def __matmul__(self, other):
        return self.value @ other

    def __rmatmul__(self, other):
        return other @ self.value

    def __imatmul__(self, other):
        self.value @= other
        return self

    def __truediv__(self, other):
        return self.value / other

    def __rtruediv__(self, other):
        return other / self.value

    def __itruediv__(self, other):
        self.value /= other
        return self

    def __floordiv__(self, other):
        return self.value // other

    def __rfloordiv__(self, other):
        return other // self.value

    def __ifloordiv__(self, other):
        self.value //= other
        return self

    def __mod__(self, other):
        return self.value % other

    def __rmod__(self, other):
        return other % self.value

    def __imod__(self, other):
        self.value %= other
        return self

    def __divmod__(self, other):
        return divmod(self.value, other)

    def __rdivmod__(self, other):
        return divmod(other, self.value)

    def __pow__(self, other):
        return self.value**other

    def __rpow__(self, other):
        return other**self.value

    def __ipow__(self, other):
        self.value **= other
        return self

    def __lshift__(self, other):
        return self.value << other

    def __rlshift__(self, other):
        return other << self.value

    def __ilshift__(self, other):
        self.value <<= other
        return self

    def __rshift__(self, other):
        return self.value >> other

    def __rrshift__(self, other):
        return other >> self.value

    def __irshift__(self, other):
        self.value >>= other
        return self

    def __and__(self, other):
        return self.value & other

    def __rand__(self, other):
        return other & self.value

    def __iand__(self, other):
        self.value &= other
        return self

    def __xor__(self, other):
        return self.value ^ other

    def __rxor__(self, other):
        return other ^ self.value

    def __ixor__(self, other):
        self.value ^= other
        return self

    def __or__(self, other):
        return self.value | other

    def __ror__(self, other):
        return other | self.value

    def __ior__(self, other):
        self.value |= other
        return self

    def __neg__(self):
        return -self.value

    def __pos__(self):
        return +self.value

    def __abs__(self):
        return abs(self.value)

    def __invert__(self):
        return ~self.value
