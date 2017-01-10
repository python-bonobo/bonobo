def run(*chain, plugins=None, strategy=None):
    from bonobo import Graph, ThreadPoolExecutorStrategy

    if len(chain) == 1 and isinstance(chain[0], Graph):
        graph = chain[0]
    elif len(chain) >= 1:
        graph = Graph()
        graph.add_chain(*chain)
    else:
        raise RuntimeError('Empty chain.')

    executor = (strategy or ThreadPoolExecutorStrategy)()
    return executor.execute(graph, plugins=plugins or [])


def console_run(*chain, output=True, plugins=None, strategy=None):
    from bonobo.ext.console import ConsoleOutputPlugin

    return run(*chain, plugins=(plugins or []) + [ConsoleOutputPlugin()] if output else [], strategy=strategy)


def jupyter_run(*chain, plugins=None, strategy=None):
    from bonobo.ext.jupyter import JupyterOutputPlugin

    return run(*chain, plugins=(plugins or []) + [JupyterOutputPlugin()], strategy=strategy)
