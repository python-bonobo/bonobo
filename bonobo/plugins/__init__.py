class Plugin:
    """
    A plugin is an extension to the core behavior of bonobo. If you're writing transformations, you should not need
    to use this interface.

    For examples, you can read bonobo.plugins.console.ConsoleOutputPlugin, or bonobo.plugins.jupyter.JupyterOutputPlugin
    that respectively permits an interactive output on an ANSI console and a rich output in a jupyter notebook. Note
    that you most probably won't instanciate them by yourself at runtime, as it's the default behaviour of bonobo to use
    them if your in a compatible context (aka an interactive terminal for the console plugin, or a jupyter notebook for
    the notebook plugin.)

    Warning: THE PLUGIN API IS PRE-ALPHA AND WILL EVOLVE BEFORE 1.0, DO NOT RELY ON IT BEING STABLE!

    """

    def register(self, dispatcher):
        """
        :param dispatcher: whistle.EventDispatcher
        """
        pass

    def unregister(self, dispatcher):
        """
        :param dispatcher: whistle.EventDispatcher
        """
        pass
