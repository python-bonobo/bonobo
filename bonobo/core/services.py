import functools

import itertools
from functools import partial


class service:
    def __init__(self, factory):
        self.factory = factory
        self.instance = None
        # self.__call__ = functools.wraps(self.__call__)

        self.children = set()

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = self.factory(*args, **kwargs)
        return self.instance

    def __getitem__(self, item):
        if item not in self.children:
            raise KeyError(item)
        return item

    def define(self, *args, **kwargs):
        new_service = type(self)(partial(self.factory, *args, **kwargs))
        self.children.add(new_service)
        return new_service


call = lambda s: s()


def resolve(func):
    return func()


def inject(*iargs, **ikwargs):
    """
    Inject service dependencies.

    TODO: ikwargs are ignored, implement that
    """

    def wrapper(target):
        @functools.wraps(target)
        def wrapped(*args, **kwargs):
            return target(*itertools.chain(map(resolve, iargs), args),
                          **{ ** kwargs, ** {k: resolve(v)
                                             for k, v in ikwargs.items()}})

        return wrapped

    return wrapper
