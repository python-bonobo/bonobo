import argparse

from stevedore import ExtensionManager


def entrypoint():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    def register_extension(ext):
        parser = subparsers.add_parser(ext.name)
        command = ext.plugin(parser)
        parser.set_defaults(command=command)

    mgr = ExtensionManager(namespace='bonobo.commands', )
    mgr.map(register_extension)

    args = parser.parse_args().__dict__
    command = args.pop('command')
    command(**args)
