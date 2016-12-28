from bonobo.core.plugins import Plugin
from bonobo.ext.jupyter.widget import BonoboWidget

try:
    import IPython.core.display
except ImportError as e:
    import logging

    logging.exception('You must install Jupyter to use the bonobo Jupyter extension. Easiest way is to install the '
                      'optional "jupyter" dependencies with «pip install bonobo[jupyter]», but you can also install a '
                      'specific version by yourself.')


class JupyterOutputPlugin(Plugin):
    def initialize(self, context):
        self.widget = BonoboWidget()
        IPython.core.display.display(self.widget)

    def run(self, context):
        self.widget.value = [repr(component) for component in context.parent.components]

    finalize = run
