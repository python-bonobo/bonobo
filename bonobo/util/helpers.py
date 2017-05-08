from bonobo.util.compat import deprecated


@deprecated
def console_run(*chain, output=True, plugins=None, strategy=None):
    from bonobo import run
    from bonobo.ext.console import ConsoleOutputPlugin

    return run(*chain, plugins=(plugins or []) + [ConsoleOutputPlugin()] if output else [], strategy=strategy)


@deprecated
def jupyter_run(*chain, plugins=None, strategy=None):
    from bonobo import run
    from bonobo.ext.jupyter import JupyterOutputPlugin

    return run(*chain, plugins=(plugins or []) + [JupyterOutputPlugin()], strategy=strategy)
