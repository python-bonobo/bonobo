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

                def call(self, s):
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

        self.__doc__ = __doc__ or self.__doc__

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

    """

    def __init__(self, *, required=True, positional=True):
        super().__init__(None, required=required, positional=positional)

    def __set__(self, inst, value):
        if not hasattr(value, '__call__'):
            raise TypeError(
                'Option of type {!r} is expecting a callable value, got {!r} object (which is not).'.format(
                    type(self).__name__, type(value).__name__
                )
            )
        inst._options_values[self.name] = self.type(value) if self.type else value

    def __call__(self, *args, **kwargs):
        # only here to trick IDEs into thinking this is callable.
        raise NotImplementedError('You cannot call the descriptor')
