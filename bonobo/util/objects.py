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
