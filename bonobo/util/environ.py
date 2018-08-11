import argparse
import codecs
import os
import re
import warnings
from contextlib import contextmanager

__escape_decoder = codecs.getdecoder('unicode_escape')
__posix_variable = re.compile('\$\{[^\}]*\}')


def parse_var(var):
    name, value = var.split('=', 1)

    def decode_escaped(escaped):
        return __escape_decoder(escaped)[0]

    if len(value) > 1:
        c = value[0]

        if c in ['"', "'"] and value[-1] == c:
            value = decode_escaped(value[1:-1])

    return name, value


def load_env_from_file(filename):
    """
    Read an env file into a collection of (name, value) tuples.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError('Environment file {} does not exist.'.format(filename))

    with open(filename) as f:
        for lineno, line in enumerate(f):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                raise SyntaxError('Invalid environment file syntax in {} at line {}.'.format(filename, lineno + 1))

            name, value = parse_var(line)

            yield name, value


_parser = None


def get_argument_parser(parser=None):
    """
    Creates an argument parser with arguments to override the system environment.

    :api: bonobo.get_argument_parser

    :param _parser:
    :return:
    """
    if parser is None:
        parser = argparse.ArgumentParser()

    # Store globally to be able to warn the user about the fact he's probably wrong not to pass a parser to
    # parse_args(), later.
    global _parser
    _parser = parser

    _parser.add_argument('--default-env-file', '-E', action='append')
    _parser.add_argument('--default-env', action='append')
    _parser.add_argument('--env-file', action='append')
    _parser.add_argument('--env', '-e', action='append')

    return _parser


@contextmanager
def parse_args(mixed=None):
    """
    Context manager to extract and apply environment related options from the provided argparser result.

    A dictionnary with unknown options will be yielded, so the remaining options can be used by the caller.

    :api: bonobo.patch_environ

    :param mixed: ArgumentParser instance, Namespace, or dict.
    :return:
    """

    if mixed is None:
        global _parser
        if _parser is not None:
            warnings.warn(
                'You are calling bonobo.parse_args() without a parser argument, but it looks like you created a parser before. You probably want to pass your parser to this call, or if creating a new parser here is really what you want to do, please create a new one explicitely to silence this warning.'
            )
        # use the api from bonobo namespace, in case a command patched it.
        import bonobo

        mixed = bonobo.get_argument_parser()

    if isinstance(mixed, argparse.ArgumentParser):
        options = mixed.parse_args()
    else:
        options = mixed

    if not isinstance(options, dict):
        options = options.__dict__

    # make a copy so we don't polute our parent variables.
    options = dict(options)

    # storage for values before patch.
    _backup = {}

    # Priority order: --env > --env-file > system > --default-env > --default-env-file
    #
    # * The code below is reading default-env before default-env-file as if the first sets something, default-env-file
    #   won't override it.
    # * Then, env-file is read from before env, as the behaviour will be the oposite (env will override a var even if
    #   env-file sets something.)
    try:
        # Set default environment
        for name, value in map(parse_var, options.pop('default_env', []) or []):
            if not name in os.environ:
                if not name in _backup:
                    _backup[name] = os.environ.get(name, None)
                os.environ[name] = value

        # Read and set default environment from file(s)
        for filename in options.pop('default_env_file', []) or []:
            for name, value in load_env_from_file(filename):
                if not name in os.environ:
                    if not name in _backup:
                        _backup[name] = os.environ.get(name, None)
                    os.environ[name] = value

        # Read and set environment from file(s)
        for filename in options.pop('env_file', []) or []:
            for name, value in load_env_from_file(filename):
                if not name in _backup:
                    _backup[name] = os.environ.get(name, None)
                os.environ[name] = value

        # Set environment
        for name, value in map(parse_var, options.pop('env', []) or []):
            if not name in _backup:
                _backup[name] = os.environ.get(name, None)
            os.environ[name] = value

        yield options
    finally:
        for name, value in _backup.items():
            if value is None:
                del os.environ[name]
            else:
                os.environ[name] = value


@contextmanager
def change_working_directory(path):
    old_dir = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(old_dir)
