from bonobo.util import get_name


class InactiveIOError(IOError):
    pass


class InactiveReadableError(InactiveIOError):
    pass


class InactiveWritableError(InactiveIOError):
    pass


class ValidationError(RuntimeError):
    def __init__(self, inst, message):
        super(ValidationError, self).__init__(
            'Validation error in {class_name}: {message}'.format(class_name=type(inst).__name__, message=message)
        )


class ProhibitedOperationError(RuntimeError):
    pass


class ConfigurationError(Exception):
    pass


class UnrecoverableError(Exception):
    """Flag for errors that must interrupt the workflow, either because they will happen for sure on each node run, or
    because you know that your transformation has no point continuing runnning after a bad event."""


class AbstractError(UnrecoverableError, NotImplementedError):
    """Abstract error is a convenient error to declare a method as "being left as an exercise for the reader"."""

    def __init__(self, method):
        super().__init__(
            'Call to abstract method {class_name}.{method_name}(...): missing implementation.'.format(
                class_name=get_name(method.__self__), method_name=get_name(method)
            )
        )


class UnrecoverableTypeError(UnrecoverableError, TypeError):
    pass


class UnrecoverableValueError(UnrecoverableError, ValueError):
    pass


class UnrecoverableRuntimeError(UnrecoverableError, RuntimeError):
    pass


class UnrecoverableNotImplementedError(UnrecoverableError, NotImplementedError):
    pass


class MissingServiceImplementationError(UnrecoverableError, KeyError):
    pass
