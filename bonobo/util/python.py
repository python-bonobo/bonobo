import inspect
import os
import runpy


class _RequiredModule:
    def __init__(self, dct):
        self.__dict__ = dct


class _RequiredModulesRegistry(dict):
    @property
    def pathname(self):
        return os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.stack()[2][0])))

    def require(self, name):
        if name not in self:
            bits = name.split('.')
            filename = os.path.join(self.pathname, *bits[:-1], bits[-1] + '.py')
            self[name] = _RequiredModule(runpy.run_path(filename, run_name=name))
        return self[name]


class WorkingDirectoryModulesRegistry(_RequiredModulesRegistry):
    @property
    def pathname(self):
        return os.getcwd()


registry = _RequiredModulesRegistry()
require = registry.require
