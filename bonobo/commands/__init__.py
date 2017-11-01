import argparse
import traceback

from bonobo import settings, logging
from bonobo.commands.base import BaseCommand, BaseGraphCommand
from bonobo.util.errors import print_error

logger = logging.get_logger()


def entrypoint(args=None):
    """
    Main callable for "bonobo" entrypoint.

    Will load commands from "bonobo.commands" entrypoints, using stevedore.

    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-D', action='store_true')

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    commands = {}

    def register_extension(ext, commands=commands):
        try:
            parser = subparsers.add_parser(ext.name)
            if isinstance(ext.plugin, type) and issubclass(ext.plugin, BaseCommand):
                # current way, class based.
                cmd = ext.plugin()
                cmd.add_arguments(parser)
                cmd.__name__ = ext.name
                commands[ext.name] = cmd.handle
            else:
                # old school, function based.
                commands[ext.name] = ext.plugin(parser)
        except Exception:
            logger.exception('Error while loading command {}.'.format(ext.name))

    from stevedore import ExtensionManager
    mgr = ExtensionManager(namespace='bonobo.commands')
    mgr.map(register_extension)

    parsed_args = parser.parse_args(args).__dict__

    if parsed_args.pop('debug', False):
        settings.DEBUG.set(True)
        settings.LOGGING_LEVEL.set(logging.DEBUG)
        logging.set_level(settings.LOGGING_LEVEL.get())

    logger.debug('Command: ' + parsed_args['command'] + ' Arguments: ' + repr(parsed_args))

    # Get command handler, execute, rince.
    command = commands[parsed_args.pop('command')]

    try:
        command(**parsed_args)
    except Exception as exc:
        print_error(exc, traceback.format_exc())
        return 255
