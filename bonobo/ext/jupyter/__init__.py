from .plugin import JupyterOutputPlugin


def _jupyter_nbextension_paths():
    return [{'section': 'notebook', 'src': 'static', 'dest': 'bonobo-jupyter', 'require': 'bonobo-jupyter/extension'}]


__all__ = [
    'JupyterOutputPlugin',
]
