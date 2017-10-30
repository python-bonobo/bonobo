import argparse
import codecs
import os
import os.path
import runpy
import sys
from contextlib import contextmanager

from bonobo import settings, logging, get_argument_parser, patch_environ
from bonobo.constants import DEFAULT_SERVICES_FILENAME, DEFAULT_SERVICES_ATTR
from bonobo.util import get_name

logger = logging.get_logger()


class BaseCommand:
    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = logging.get_logger(get_name(self))
            return self._logger

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this method.
        """
        raise NotImplementedError('Subclasses of BaseCommand must provide a handle() method')


class BaseGraphCommand(BaseCommand):
    required = True

    def add_arguments(self, parser):
        # target arguments (cannot provide both).
        source_group = parser.add_mutually_exclusive_group(required=self.required)
        source_group.add_argument('file', nargs='?', type=str)
        source_group.add_argument('-m', dest='mod', type=str)

        # add arguments to enforce system environment.
        parser = get_argument_parser(parser)

        return parser

    def _run_path(self, file):
        return runpy.run_path(file, run_name='__main__')

    def _run_module(self, mod):
        return runpy.run_module(mod, run_name='__main__')

    def read(self, *, file, mod, args=None, **options):
        _graph, _options = None, None

        def _record(graph, **options):
            nonlocal _graph, _options
            _graph, _options = graph, options

        with _override_runner(_record), patch_environ(options):
            _argv = sys.argv
            try:
                if file:
                    sys.argv = [file] + list(args) if args else [file]
                    self._run_path(file)
                elif mod:
                    sys.argv = [mod, *(args or ())]
                    self._run_module(mod)
                else:
                    raise RuntimeError('No target provided.')
            finally:
                sys.argv = _argv

        if _graph is None:
            raise RuntimeError('Could not find graph.')

        return _graph, _options

    def handle(self, *args, **options):
        pass


def entrypoint(args=None):
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

    parsed_args, remaining = parser.parse_known_args(args)
    parsed_args = parsed_args.__dict__

    if parsed_args.pop('debug', False):
        settings.DEBUG.set(True)
        settings.LOGGING_LEVEL.set(logging.DEBUG)
        logging.set_level(settings.LOGGING_LEVEL.get())

    logger.debug('Command: ' + parsed_args['command'] + ' Arguments: ' + repr(parsed_args))

    # Get command handler
    command = commands[parsed_args.pop('command')]

    if len(remaining):
        command(_remaining_args=remaining, **parsed_args)
    else:
        command(**parsed_args)


@contextmanager
def _override_runner(runner):
    import bonobo
    _get_argument_parser = bonobo.get_argument_parser
    _run = bonobo.run
    try:
        def get_argument_parser(parser=None):
            return parser or argparse.ArgumentParser()

        bonobo.get_argument_parser = get_argument_parser
        bonobo.run = runner

        yield runner
    finally:
        bonobo.get_argument_parser = _get_argument_parser
        bonobo.run = _run


def set_env_var(e, override=False):
    __escape_decoder = codecs.getdecoder('unicode_escape')
    ename, evalue = e.split('=', 1)

    def decode_escaped(escaped):
        return __escape_decoder(escaped)[0]

    if len(evalue) > 0:
        if evalue[0] == evalue[len(evalue) - 1] in ['"', "'"]:
            evalue = decode_escaped(evalue[1:-1])

    if override:
        os.environ[ename] = evalue
    else:
        os.environ.setdefault(ename, evalue)
