from bonobo.ext.jupyter.widget import BonoboWidget
from bonobo.plugins import Plugin

try:
    import IPython.core.display
except ImportError as e:
    import logging

    logging.exception(
        'You must install Jupyter to use the bonobo Jupyter extension. Easiest way is to install the '
        'optional "jupyter" dependencies with «pip install bonobo[jupyter]», but you can also install a '
        'specific version by yourself.'
    )


class JupyterOutputPlugin(Plugin):
    def initialize(self):
        self.widget = BonoboWidget()
        IPython.core.display.display(self.widget)

    def run(self):
        self.widget.value = [
            str(self.context.parent[i]) for i in self.context.parent.graph.topologically_sorted_indexes
        ]

    finalize = run
