from bonobo.config.options import Option

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

        for typ in cls.__mro__:
            for name, value in typ.__dict__.items():
                if isinstance(value, Option):
                    if not value.name:
                        value.name = name
                    if not name in cls.__options__:
                        cls.__options__[name] = value
                    if value.positional:
                        cls.__positional_options__.append(name)


class Configurable(metaclass=ConfigurableMeta):
    """
    Generic class for configurable objects. Configurable objects have a dictionary of "options" descriptors that defines
    the configuration schema of the type.

    """

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
            if positional_option in missing:
                kwargs[positional_option] = args[position]
                position += 1
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
