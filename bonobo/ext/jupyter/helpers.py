from bonobo import Graph, ThreadPoolExecutorStrategy
from .plugin import JupyterOutputPlugin


def jupyter_run(*chain, plugins=None):
    graph = Graph()
    executor = ThreadPoolExecutorStrategy()
    graph.add_chain(*chain)
    return executor.execute(graph, plugins=(plugins or []) + [JupyterOutputPlugin()])
