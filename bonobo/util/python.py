import inspect
import os
import runpy


class _RequiredModule:
    def __init__(self, dct):
        self.__dict__ = dct


class _RequiredModulesRegistry(dict):
    def require(self, name):
        if name not in self:
            bits = name.split('.')
            pathname = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.stack()[1][0])))
            filename = os.path.join(pathname, *bits[:-1], bits[-1] + '.py')
            self[name] = _RequiredModule(runpy.run_path(filename, run_name=name))
        return self[name]


registry = _RequiredModulesRegistry()
require = registry.require
