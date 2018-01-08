import logging

from bonobo.contrib.jupyter.widget import BonoboWidget
from bonobo.execution import events
from bonobo.plugins import Plugin

try:
    import IPython.core.display
except ImportError as e:
    logging.exception(
        'You must install Jupyter to use the bonobo Jupyter extension. Easiest way is to install the '
        'optional "jupyter" dependencies with «pip install bonobo[jupyter]», but you can also install a '
        'specific version by yourself.'
    )


class JupyterOutputPlugin(Plugin):
    def register(self, dispatcher):
        dispatcher.add_listener(events.START, self.setup)
        dispatcher.add_listener(events.TICK, self.tick)
        dispatcher.add_listener(events.STOPPED, self.tick)

    def unregister(self, dispatcher):
        dispatcher.remove_listener(events.STOPPED, self.tick)
        dispatcher.remove_listener(events.TICK, self.tick)
        dispatcher.remove_listener(events.START, self.setup)

    def setup(self, event):
        self.widget = BonoboWidget()
        IPython.core.display.display(self.widget)

    def tick(self, event):
        self.widget.value = [event.context[i].as_dict() for i in event.context.graph.topologically_sorted_indexes]
