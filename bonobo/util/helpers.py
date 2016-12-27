def run(*chain, plugins=None):
    from bonobo import Graph, ThreadPoolExecutorStrategy

    graph = Graph()
    graph.add_chain(*chain)

    executor = ThreadPoolExecutorStrategy()
    return executor.execute(graph, plugins=plugins or [])


def console_run(*chain, output=True, plugins=None):
    from bonobo.ext.console import ConsoleOutputPlugin

    return run(*chain, plugins=(plugins or []) + [ConsoleOutputPlugin()] if output else [])


def jupyter_run(*chain, plugins=None):
    from bonobo.ext.jupyter import JupyterOutputPlugin

    return run(*chain, plugins=(plugins or []) + [JupyterOutputPlugin()])
