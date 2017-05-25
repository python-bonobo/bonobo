from bonobo.config.options import Method, Option
from bonobo.config.processors import ContextProcessor
from bonobo.errors import ConfigurationError, AbstractError

__all__ = [
    'Configurable',
    'Option',
]


class ConfigurableMeta(type):
    """
    Metaclass for Configurables that will add options to a special __options__ dict.
    """

    def __init__(cls, what, bases=None, dict=None):
        super().__init__(what, bases, dict)
        cls.__options__ = {}
        cls.__positional_options__ = []
        cls.__processors__ = []
        cls.__wrappable__ = None

        for typ in cls.__mro__:
            for name, value in typ.__dict__.items():
                if isinstance(value, Option):
                    if isinstance(value, ContextProcessor):
                        cls.__processors__.append(value)
                    else:
                        if not value.name:
                            value.name = name

                        if isinstance(value, Method):
                            if cls.__wrappable__:
                                raise ConfigurationError(
                                    'Cannot define more than one "Method" option in a configurable. That may change in the future.'
                                )
                            cls.__wrappable__ = name

                        if not name in cls.__options__:
                            cls.__options__[name] = value

                        if value.positional:
                            cls.__positional_options__.append(name)

        # This can be done before, more efficiently. Not so bad neither as this is only done at type() creation time
        # (aka class Xxx(...) time) and there should not be hundreds of processors. Still not very elegant.
        cls.__processors__ = sorted(cls.__processors__, key=lambda v: v._creation_counter)


class Configurable(metaclass=ConfigurableMeta):
    """
    Generic class for configurable objects. Configurable objects have a dictionary of "options" descriptors that defines
    the configuration schema of the type.

    """

    def __new__(cls, *args, **kwargs):
        if cls.__wrappable__ and len(args) == 1 and hasattr(args[0], '__call__'):
            return type(args[0].__name__, (cls, ), {cls.__wrappable__: args[0]})

        return super(Configurable, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        super().__init__()

        # initialize option's value dictionary, used by descriptor implementation (see Option).
        self.__options_values__ = {}

        # compute missing options, given the kwargs.
        missing = set()
        for name, option in type(self).__options__.items():
            if option.required and not option.name in kwargs:
                missing.add(name)

        # transform positional arguments in keyword arguments if possible.
        position = 0
        for positional_option in self.__positional_options__:
            if len(args) <= position:
                break
            kwargs[positional_option] = args[position]
            position += 1
            if positional_option in missing:
                missing.remove(positional_option)

        # complain if there are still missing options.
        if len(missing):
            raise TypeError(
                '{}() missing {} required option{}: {}.'.format(
                    type(self).__name__,
                    len(missing), 's' if len(missing) > 1 else '', ', '.join(map(repr, sorted(missing)))
                )
            )

        # complain if there is more options than possible.
        extraneous = set(kwargs.keys()) - set(type(self).__options__.keys())
        if len(extraneous):
            raise TypeError(
                '{}() got {} unexpected option{}: {}.'.format(
                    type(self).__name__,
                    len(extraneous), 's' if len(extraneous) > 1 else '', ', '.join(map(repr, sorted(extraneous)))
                )
            )

        # set option values.
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __call__(self, *args, **kwargs):
        """ You can implement a configurable callable behaviour by implemenenting the call(...) method. Of course, it is also backward compatible with legacy __call__ override.
        """
        return self.call(*args, **kwargs)

    def call(self, *args, **kwargs):
        raise AbstractError('Not implemented.')
