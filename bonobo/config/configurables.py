from bonobo.util.inspect import isoption, iscontextprocessor
from bonobo.errors import AbstractError
from bonobo.util.collections import sortedlist

__all__ = [
    'Configurable',
    'Option',
]

get_creation_counter = lambda v: v._creation_counter


class ConfigurableMeta(type):
    """
    Metaclass for Configurables that will add options to a special __options__ dict.
    """

    def __init__(cls, what, bases=None, dict=None):
        super().__init__(what, bases, dict)

        cls.__processors = sortedlist()
        cls.__methods = sortedlist()
        cls.__options = sortedlist()
        cls.__names = set()

        # cls.__kwoptions = []

        for typ in cls.__mro__:
            for name, value in filter(lambda x: isoption(x[1]), typ.__dict__.items()):
                if iscontextprocessor(value):
                    cls.__processors.insort((value._creation_counter, value))
                    continue

                if not value.name:
                    value.name = name

                if not name in cls.__names:
                    cls.__names.add(name)
                    cls.__options.insort((not value.positional, value._creation_counter, name, value))

    @property
    def __options__(cls):
        return ((name, option) for _, _, name, option in cls.__options)

    @property
    def __options_dict__(cls):
        return dict(cls.__options__)

    @property
    def __processors__(cls):
        return (processor for _, processor in cls.__processors)

    def __repr__(self):
        return ' '.join(('<Configurable', super(ConfigurableMeta, self).__repr__().split(' ', 1)[1], ))


try:
    import _functools
except:
    import functools

    PartiallyConfigured = functools.partial
else:

    class PartiallyConfigured(_functools.partial):
        @property  # TODO XXX cache this shit
        def _options_values(self):
            """ Simulate option values for partially configured objects. """
            try:
                return self.__options_values
            except AttributeError:
                self.__options_values = {**self.keywords}

                position = 0

                for name, option in self.func.__options__:
                    if not option.positional:
                        break  # no positional left
                    if name in self.keywords:
                        continue  # already fulfilled

                    self.__options_values[name] = self.args[position] if len(self.args) >= position + 1 else None
                    position += 1

                return self.__options_values

        def __getattr__(self, item):
            _dict = self.func.__options_dict__
            if item in _dict:
                return _dict[item].__get__(self, self.func)
            return getattr(self.func, item)


class Configurable(metaclass=ConfigurableMeta):
    """
    Generic class for configurable objects. Configurable objects have a dictionary of "options" descriptors that defines
    the configuration schema of the type.

    """

    def __new__(cls, *args, _final=False, **kwargs):
        """
        Custom instance builder. If not all options are fulfilled, will return a :class:`PartiallyConfigured` instance
        which is just a :class:`functools.partial` object that behaves like a :class:`Configurable` instance.

        The special `_final` argument can be used to force final instance to be created, or an error raised if options
        are missing.

        :param args:
        :param _final: bool
        :param kwargs:
        :return: Configurable or PartiallyConfigured
        """
        options = tuple(cls.__options__)
        # compute missing options, given the kwargs.
        missing = set()
        for name, option in options:
            if option.required and not option.name in kwargs:
                missing.add(name)

        # transform positional arguments in keyword arguments if possible.
        position = 0
        for name, option in options:
            if not option.positional:
                break  # option orders make all positional options first, job done.

            if not isoption(getattr(cls, name)):
                missing.remove(name)
                continue

            if len(args) <= position:
                break  # no more positional arguments given.

            position += 1
            if name in missing:
                missing.remove(name)

        # complain if there is more options than possible.
        extraneous = set(kwargs.keys()) - (set(next(zip(*options))) if len(options) else set())
        if len(extraneous):
            raise TypeError(
                '{}() got {} unexpected option{}: {}.'.format(
                    cls.__name__,
                    len(extraneous), 's' if len(extraneous) > 1 else '', ', '.join(map(repr, sorted(extraneous)))
                )
            )

        # missing options? we'll return a partial instance to finish the work later, unless we're required to be
        # "final".
        if len(missing):
            if _final:
                raise TypeError(
                    '{}() missing {} required option{}: {}.'.format(
                        cls.__name__,
                        len(missing), 's' if len(missing) > 1 else '', ', '.join(map(repr, sorted(missing)))
                    )
                )
            return PartiallyConfigured(cls, *args, **kwargs)

        return super(Configurable, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        # initialize option's value dictionary, used by descriptor implementation (see Option).
        self._options_values = {**kwargs}

        # set option values.
        for name, value in kwargs.items():
            setattr(self, name, value)

        position = 0
        for name, option in self.__options__:
            if not option.positional:
                break  # option orders make all positional options first

            # value was overriden? Skip.
            maybe_value = getattr(type(self), name)
            if not isoption(maybe_value):
                continue

            if len(args) <= position:
                break

            if name in self._options_values:
                raise ValueError('Already got a value for option {}'.format(name))

            setattr(self, name, args[position])
            position += 1

    def __call__(self, *args, **kwargs):
        """ You can implement a configurable callable behaviour by implemenenting the call(...) method. Of course, it is also backward compatible with legacy __call__ override.
        """
        return self.call(*args, **kwargs)

    @property
    def __options__(self):
        return type(self).__options__

    @property
    def __processors__(self):
        return type(self).__processors__

    def call(self, *args, **kwargs):
        raise AbstractError('Not implemented.')
