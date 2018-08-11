from collections import namedtuple


def isconfigurable(mixed):
    """
    Check if the given argument is an instance of :class:`bonobo.config.Configurable`.

    :param mixed:
    :return: bool
    """
    from bonobo.config.configurables import Configurable

    return isinstance(mixed, Configurable)


def isconfigurabletype(mixed, *, strict=False):
    """
    Check if the given argument is an instance of :class:`bonobo.config.ConfigurableMeta`, meaning it has all the
    plumbery necessary to build :class:`bonobo.config.Configurable`-like instances.

    :param mixed:
    :param strict: should we consider partially configured objects?
    :return: bool
    """
    from bonobo.config.configurables import ConfigurableMeta, PartiallyConfigured

    if isinstance(mixed, ConfigurableMeta):
        return True

    if strict:
        return False

    if isinstance(mixed, PartiallyConfigured):
        return True

    if hasattr(mixed, '_partial') and mixed._partial:
        return True

    return False


def isoption(mixed):
    """
    Check if the given argument is an instance of :class:`bonobo.config.Option`.

    :param mixed:
    :return: bool
    """

    from bonobo.config.options import Option

    return isinstance(mixed, Option)


def ismethod(mixed):
    """
    Check if the given argument is an instance of :class:`bonobo.config.Method`.

    :param mixed:
    :return: bool
    """
    from bonobo.config.options import Method

    return isinstance(mixed, Method)


def iscontextprocessor(x):
    """
    Check if the given argument is an instance of :class:`bonobo.config.ContextProcessor`.

    :param mixed:
    :return: bool
    """
    from bonobo.config.processors import ContextProcessor

    return isinstance(x, ContextProcessor)


def istype(mixed):
    """
    Check if the given argument is a type object.

    :param mixed:
    :return: bool
    """
    return isinstance(mixed, type)


def isdict(mixed):
    """
    Check if the given argument is a dict.

    :param mixed:
    :return: bool
    """
    return isinstance(mixed, dict)


def istuple(mixed):
    """
    Check if the given argument is a tuple.

    :param mixed:
    :return: bool
    """
    return isinstance(mixed, tuple)


ConfigurableInspection = namedtuple('ConfigurableInspection', ['type', 'instance', 'options', 'processors', 'partial'])

ConfigurableInspection.__enter__ = lambda self: self
ConfigurableInspection.__exit__ = lambda *exc_details: None


def inspect_node(mixed, *, _partial=None):
    """
    If the given argument is somehow a :class:`bonobo.config.Configurable` object (either a subclass, an instance, or
    a partially configured instance), then it will return a :class:`ConfigurableInspection` namedtuple, used to inspect
    the configurable metadata (options). If you want to get the option values, you don't need this, it is only usefull
    to perform introspection on a configurable.

    If it's not looking like a configurable, it will raise a :class:`TypeError`.

    :param mixed:
    :return: ConfigurableInspection

    :raise: TypeError
    """
    if isconfigurabletype(mixed, strict=True):
        inst, typ = None, mixed
    elif isconfigurable(mixed):
        inst, typ = mixed, type(mixed)
    elif hasattr(mixed, 'func'):
        return inspect_node(mixed.func, _partial=(mixed.args, mixed.keywords))
    else:
        raise TypeError(
            'Not a Configurable, nor a Configurable instance and not even a partially configured Configurable. Check your inputs.'
        )

    return ConfigurableInspection(typ, inst, list(typ.__options__), list(typ.__processors__), _partial)
