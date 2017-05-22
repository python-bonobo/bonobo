from bonobo.config import Configurable
from bonobo.util.objects import get_attribute_or_create


class Plugin:
    """
    A plugin is an extension to the core behavior of bonobo. If you're writing transformations, you should not need
    to use this interface.
    
    For examples, you can read bonobo.ext.console.ConsoleOutputPlugin, or bonobo.ext.jupyter.JupyterOutputPlugin that
    respectively permits an interactive output on an ANSI console and a rich output in a jupyter notebook.
    
    Warning: THE PLUGIN API IS PRE-ALPHA AND WILL EVOLVE BEFORE 1.0, DO NOT RELY ON IT BEING STABLE!
    
    """

    def __init__(self, context):
        self.context = context

    def initialize(self):
        pass

    def run(self):
        pass

    def finalize(self):
        pass


def get_enhancers(obj):
    try:
        return get_attribute_or_create(obj, '__enhancers__', list())
    except AttributeError:
        return list()


class NodeEnhancer(Configurable):
    def __matmul__(self, other):
        get_enhancers(other).append(self)
        return other
