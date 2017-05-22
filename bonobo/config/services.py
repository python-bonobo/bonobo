import re
import types

from bonobo.config.options import Option

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
        return services.get(getattr(inst, self.name))


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
            raise KeyError('Cannot resolve service {!r} using provided service collection.'.format(name))
        value = super().get(name)
        if isinstance(value, types.LambdaType):
            value = value(self)
        return value
