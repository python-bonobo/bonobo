from bonobo import Graph, ThreadPoolExecutorStrategy
from .plugin import ConsoleOutputPlugin


def console_run(*chain, output=True, plugins=None):
    graph = Graph()
    executor = ThreadPoolExecutorStrategy()
    graph.add_chain(*chain)
    return executor.execute(graph, plugins=(plugins or []) + [ConsoleOutputPlugin()] if output else [])
