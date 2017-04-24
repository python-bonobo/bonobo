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
    def __init__(self, value, *, type=None):
        self.value = value
        self.type = type

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

    def __sub__(self, other):
        return self.value - other

    def __rsub__(self, other):
        return other - self.value

    def __isub__(self, other):
        self.value -= other

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __imul__(self, other):
        self.value *= other

    def __matmul__(self, other):
        return self.value @ other

    def __rmatmul__(self, other):
        return other @ self.value

    def __imatmul__(self, other):
        self.value @= other

    def __truediv__(self, other):
        return self.value / other

    def __rtruediv__(self, other):
        return other / self.value

    def __itruediv__(self, other):
        self.value /= other

"""
object.__matmul__(self, other)
object.__truediv__(self, other)
object.__floordiv__(self, other)
object.__mod__(self, other)
object.__divmod__(self, other)
object.__pow__(self, other[, modulo])
object.__lshift__(self, other)
object.__rshift__(self, other)
object.__and__(self, other)
object.__xor__(self, other)
object.__or__(self, other)

"""
