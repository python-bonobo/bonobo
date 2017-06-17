import re
import threading
import types
from contextlib import ContextDecorator

from bonobo.config.options import Option
from bonobo.errors import MissingServiceImplementationError

_service_name_re = re.compile(r"^[^\d\W]\w*(:?\.[^\d\W]\w*)*$", re.UNICODE)


def validate_service_name(name):
    if not _service_name_re.match(name):
        raise ValueError('Invalid service name {!r}.'.format(name))
    return name


class Service(Option):
    """
    A Service is a special kind of option defining a dependency to something that will be resolved at runtime, using an
    identifier. For example, you can create a Configurable that has a "database" Service in its attribute, meaning that
    you'll define which database to use, by name, when creating the instance of this class, then provide an
    implementation when running the graph using a strategy.
    
    Example::
    
        import bonobo
    
        class QueryExtractor(bonobo.Configurable):
            database = bonobo.Service(default='sqlalchemy.engine.default')
            
        graph = bonobo.Graph(
            QueryExtractor(database='sqlalchemy.engine.secondary'),
            *more_transformations,
        )
        
        if __name__ == '__main__':
            engine = create_engine('... dsn ...')
            bonobo.run(graph, services={
                'sqlalchemy.engine.secondary': engine
            })
            
    The main goal is not to tie transformations to actual dependencies, so the same can be run in different contexts
    (stages like preprod, prod, or tenants like client1, client2, or anything you want).

    .. attribute:: name

        Service name will be used to retrieve the implementation at runtime.
    
    """

    def __init__(self, name):
        super().__init__(str, required=False, default=name)

    def __set__(self, inst, value):
        inst.__options_values__[self.name] = validate_service_name(value)

    def resolve(self, inst, services):
        try:
            name = getattr(inst, self.name)
        except AttributeError:
            name = self.name
        return services.get(name)


class Container(dict):
    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            assert not len(kwargs), 'only one usage at a time, my dear.'
            if not (args[0]):
                return super().__new__(cls)
            if isinstance(args[0], cls):
                return cls
        return super().__new__(cls, *args, **kwargs)

    def args_for(self, mixed):
        try:
            options = mixed.__options__
        except AttributeError:
            options = {}

        return tuple(option.resolve(mixed, self) for name, option in options.items() if isinstance(option, Service))

    def get(self, name, default=None):
        if not name in self:
            if default:
                return default
            raise MissingServiceImplementationError(
                'Cannot resolve service {!r} using provided service collection.'.format(name)
            )
        value = super().get(name)
        # XXX this is not documented and can lead to errors.
        if isinstance(value, types.LambdaType):
            value = value(self)
        return value


class Exclusive(ContextDecorator):
    """
    Decorator and context manager used to require exclusive usage of an object, most probably a service. It's usefull
    for example if call order matters on a service implementation (think of an http api that requires a nonce or version
    parameter ...).

    Usage:

        >>> def handler(some_service):
        ...     with Exclusive(some_service):
        ...         some_service.call_1()
        ...         some_service.call_2()
        ...         some_service.call_3()

    This will ensure that nobody else is using the same service while in the "with" block, using a lock primitive to
    ensure that.

    """
    _locks = {}

    def __init__(self, wrapped):
        self._wrapped = wrapped

    def get_lock(self):
        _id = id(self._wrapped)
        if not _id in Exclusive._locks:
            Exclusive._locks[_id] = threading.RLock()
        return Exclusive._locks[_id]

    def __enter__(self):
        self.get_lock().acquire()
        return self._wrapped

    def __exit__(self, *exc):
        self.get_lock().release()


def requires(*service_names):
    def decorate(mixed):
        try:
            options = mixed.__options__
        except AttributeError:
            mixed.__options__ = options = {}

        for service_name in service_names:
            service = Service(service_name)
            service.name = service_name
            options[service_name] = service
        return mixed

    return decorate
