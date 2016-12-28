from IPython.core.display import display

from bonobo.core.plugins import Plugin
from bonobo.ext.jupyter.widget import BonoboWidget

try:
    import selenium
except ImportError as e:
    import logging

    logging.exception(
        'You must install selenium to use the bonobo selenium extension. Easiest way is to install the '
        'optional "selenium" dependencies with «pip install bonobo[selenium]», but you can also install a '
        'specific version by yourself.')


class JupyterOutputPlugin(Plugin):
    def initialize(self, context):
        self.widget = BonoboWidget()
        display(self.widget)

    def run(self, context):
        self.widget.value = [repr(component) for component in context.parent.components]

    finalize = run
