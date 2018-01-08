import ipywidgets as widgets
from traitlets import List, Unicode


@widgets.register('bonobo-widget.bonobo')
class BonoboWidget(widgets.DOMWidget):
    _view_name = Unicode('BonoboView').tag(sync=True)
    _model_name = Unicode('BonoboModel').tag(sync=True)
    _view_module = Unicode('bonobo-jupyter').tag(sync=True)
    _model_module = Unicode('bonobo-jupyter').tag(sync=True)
    value = List().tag(sync=True)
