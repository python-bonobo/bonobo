import argparse

import logging
from stevedore import ExtensionManager


def entrypoint(args=None):
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    commands = {}

    def register_extension(ext, commands=commands):
        try:
            parser = subparsers.add_parser(ext.name)
            commands[ext.name] = ext.plugin(parser)
        except Exception:
            logging.exception('Error while loading command {}.'.format(ext.name))

    mgr = ExtensionManager(
        namespace='bonobo.commands',
    )
    mgr.map(register_extension)

    args = parser.parse_args(args).__dict__
    commands[args.pop('command')](**args)
