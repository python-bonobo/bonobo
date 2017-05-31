import argparse

from bonobo import logging, settings

logger = logging.get_logger()


def entrypoint(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-D', action='store_true')

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    commands = {}

    def register_extension(ext, commands=commands):
        try:
            parser = subparsers.add_parser(ext.name)
            commands[ext.name] = ext.plugin(parser)
        except Exception:
            logger.exception('Error while loading command {}.'.format(ext.name))

    from stevedore import ExtensionManager
    mgr = ExtensionManager(namespace='bonobo.commands')
    mgr.map(register_extension)

    args = parser.parse_args(args).__dict__
    if args.pop('debug', False):
        settings.DEBUG = True
        settings.LOGGING_LEVEL = logging.DEBUG
        logging.set_level(settings.LOGGING_LEVEL)

    logger.debug('Command: ' + args['command'] + ' Arguments: ' + repr(args))
    commands[args.pop('command')](**args)
