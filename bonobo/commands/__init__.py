import argparse
import codecs
import os
import os.path
import runpy
from contextlib import contextmanager
from functools import partial

from bonobo import settings, logging
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

        # arguments to enforce system environment.
        parser.add_argument('--default-env-file', action='append')
        parser.add_argument('--default-env', action='append')
        parser.add_argument('--env-file', action='append')
        parser.add_argument('--env', '-e', action='append')

        return parser

    def _run_path(self, file):
        return runpy.run_path(file, run_name='__main__')

    def _run_module(self, mod):
        return runpy.run_module(mod, run_name='__main__')

    def read(self, *, file, mod, **options):

        """

        get_default_services(
            filename, context.get(DEFAULT_SERVICES_ATTR)() if DEFAULT_SERVICES_ATTR in context else None
        )
        
        """

        _graph, _options = None, None

        def _record(graph, **options):
            nonlocal _graph, _options
            _graph, _options = graph, options

        with _override_runner(_record), _override_environment():
            if file:
                self._run_path(file)
            elif mod:
                self._run_module(mod)
            else:
                raise RuntimeError('No target provided.')

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

    args = parser.parse_args(args).__dict__
    if args.pop('debug', False):
        settings.DEBUG.set(True)
        settings.LOGGING_LEVEL.set(logging.DEBUG)
        logging.set_level(settings.LOGGING_LEVEL.get())

    logger.debug('Command: ' + args['command'] + ' Arguments: ' + repr(args))
    commands[args.pop('command')](**args)


@contextmanager
def _override_runner(runner):
    import bonobo
    _runner_backup = bonobo.run
    try:
        bonobo.run = runner
        yield runner
    finally:
        bonobo.run = _runner_backup


@contextmanager
def _override_environment(root_dir=None, **options):
    yield
    return
    if default_env_file:
        for f in default_env_file:
            env_file_path = str(env_dir.joinpath(f))
            load_dotenv(env_file_path)
    if default_env:
        for e in default_env:
            set_env_var(e)
    if env_file:
        for f in env_file:
            env_file_path = str(env_dir.joinpath(f))
            load_dotenv(env_file_path, override=True)
    if env:
        for e in env:
            set_env_var(e, override=True)


def get_default_services(filename, services=None):
    dirname = os.path.dirname(filename)
    services_filename = os.path.join(dirname, DEFAULT_SERVICES_FILENAME)
    if os.path.exists(services_filename):
        with open(services_filename) as file:
            code = compile(file.read(), services_filename, 'exec')
        context = {
            '__name__': '__services__',
            '__file__': services_filename,
        }
        exec(code, context)

        return {
            **context[DEFAULT_SERVICES_ATTR](),
            **(services or {}),
        }
    return services or {}


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