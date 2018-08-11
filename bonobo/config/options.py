import textwrap
import types

from bonobo.util.inspect import istype


class Option:
    """
    An Option is a descriptor for Configurable's parameters.

    .. attribute:: type

        Option type allows to provide a callable used to cast, clean or validate the option value. If not provided, or
        None, the option's value will be the exact value user provided.

        (default: None)

    .. attribute:: required

        If an option is required, an error will be raised if no value is provided (at runtime). If it is not, option
        will have the default value if user does not override it at runtime.

        Ignored if a default is provided, meaning that the option cannot be required.

        (default: True)

    .. attribute:: positional

        If this is true, it'll be possible to provide the option value as a positional argument. Otherwise, it must
        be provided as a keyword argument.

        (default: False)

    .. attribute:: default

        Default value for non-required options.

        (default: None)

    Example:

        .. code-block:: python

            from bonobo.config import Configurable, Option

            class Example(Configurable):
                title = Option(str, required=True, positional=True)
                keyword = Option(str, default='foo')

                def __call__(self, s):
                    return self.title + ': ' + s + ' (' + self.keyword + ')'

            example = Example('hello', keyword='bar')

    """

    _creation_counter = 0

    def __init__(self, type=None, *, required=True, positional=False, default=None, __doc__=None):
        self.name = None
        self.type = type
        self.required = required if default is None else False
        self.positional = positional
        self.default = default

        # Docstring formating
        self.__doc__ = __doc__ or None
        if self.__doc__:
            self.__doc__ = textwrap.dedent(self.__doc__.strip('\n')).strip()
            if default:
                self.__doc__ += '\n\nDefault: {!r}'.format(default)

        # This hack is necessary for python3.5
        self._creation_counter = Option._creation_counter
        Option._creation_counter += 1

    def __get__(self, inst, type_):
        # XXX If we call this on the type, then either return overriden value or ... ???
        if inst is None:
            return vars(type_).get(self.name, self)

        if not self.name in inst._options_values:
            inst._options_values[self.name] = self.get_default()

        return inst._options_values[self.name]

    def __set__(self, inst, value):
        inst._options_values[self.name] = self.clean(value)

    def __repr__(self):
        return '<{positional}{typename} {type}{name} default={default!r}{required}>'.format(
            typename=type(self).__name__,
            type='({})'.format(self.type) if istype(self.type) else '',
            name=self.name,
            positional='*' if self.positional else '**',
            default=self.default,
            required=' (required)' if self.required else '',
        )

    def clean(self, value):
        return self.type(value) if self.type else value

    def get_default(self):
        return self.default() if callable(self.default) else self.default


class RemovedOption(Option):
    def __init__(self, *args, value, **kwargs):
        kwargs['required'] = False
        super(RemovedOption, self).__init__(*args, **kwargs)
        self.value = value

    def clean(self, value):
        if value != self.value:
            raise ValueError(
                'Removed options cannot change value, {!r} must now be {!r} (and you should remove setting the value explicitely, as it is deprecated and will be removed quite soon.'.format(
                    self.name, self.value
                )
            )
        return self.value

    def get_default(self):
        return self.value


class RenamedOption(Option):
    def __init__(self, target, *, positional=False):
        super(RenamedOption, self).__init__(required=False, positional=False)
        self.target = target

    def __get__(self, instance, owner):
        raise ValueError(
            'Trying to get value from renamed option {}, try getting {} instead.'.format(self.name, self.target)
        )

    def clean(self, value):
        raise ValueError(
            'Trying to set value of renamed option {}, try setting {} instead.'.format(self.name, self.target)
        )


class Method(Option):
    """
    A Method is a special callable-valued option, that can be used in three different ways (but for same purpose).

    * Like a normal option, the value can be provided to the Configurable constructor.

        >>> from bonobo.config import Configurable, Method

        >>> class MethodExample(Configurable):
        ...     handler = Method()

        >>> example1 = MethodExample(handler=str.upper)

    * It can be used by a child class that overrides the Method with a normal method.

        >>> class ChildMethodExample(MethodExample):
        ...     def handler(self, s: str):
        ...         return s.upper()

        >>> example2 = ChildMethodExample()

    * Finally, it also enables the class to be used as a decorator, to generate a subclass providing the Method a value.

        >>> @MethodExample
        ... def OtherChildMethodExample(s):
        ...     return s.upper()

        >>> example3 = OtherChildMethodExample()

    It's possible to pass a default implementation to a Method by calling it, making it suitable to use as a decorator.

        >>> class MethodExampleWithDefault(Configurable):
        ...     @Method()
        ...     def handler(self):
        ...         pass

    """

    def __init__(self, *, default=None, required=True, positional=True, __doc__=None):
        super().__init__(None, required=required, positional=positional, __doc__=__doc__)

        # If a callable is provided as default, then use self as if it was used as a decorator
        if default is not None:
            if not callable(default):
                raise ValueError('Method defaults should be callable, if provided.')
            self(default)

    def __get__(self, inst, type_):
        x = super(Method, self).__get__(inst, type_)
        if inst:
            x = types.MethodType(x, inst)
        return x

    def __set__(self, inst, value):
        if not callable(value):
            raise TypeError(
                'Option {!r} ({}) is expecting a callable value, got {!r} object: {!r}.'.format(
                    self.name, type(self).__name__, type(value).__name__, value
                )
            )
        inst._options_values[self.name] = self.type(value) if self.type else value

    def __call__(self, impl):
        if self.default:
            raise RuntimeError('Can only be used once as a decorator.')
        self.default = impl
        self.required = False
        return self

    def get_default(self):
        return self.default
