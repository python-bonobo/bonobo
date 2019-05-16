from bonobo.util import get_name


class ApiHelper:
    # TODO __all__ kwarg only
    def __init__(self, __all__):
        self.__all__ = __all__

    def register(self, x, graph=False):
        """Register a function as being part of an API, then returns the original function."""

        if graph:
            # This function must comply to the "graph" API interface, meaning it can bahave like bonobo.run.
            from inspect import signature

            parameters = list(signature(x).parameters)
            required_parameters = {'plugins', 'services', 'strategy'}
            assert (
                len(parameters) > 0 and parameters[0] == 'graph'
            ), 'First parameter of a graph api function must be "graph".'
            assert (
                required_parameters.intersection(parameters) == required_parameters
            ), 'Graph api functions must define the following parameters: ' + ', '.join(sorted(required_parameters))

        self.__all__.append(get_name(x))
        return x

    def register_graph(self, x):
        return self.register(x, graph=True)

    def register_group(self, *args, check=None):
        check = set(check) if check else None
        for attr in args:
            self.register(attr)
            if check:
                check.remove(get_name(attr))
        assert not (check and len(check))
