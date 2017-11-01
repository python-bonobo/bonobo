import functools
import io
import os
import runpy
import sys
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

import pkg_resources
import pytest

from bonobo import __main__, __version__, get_examples_path
from bonobo.commands import entrypoint
from bonobo.commands.download import EXAMPLES_BASE_URL


def runner(f):
    @functools.wraps(f)
    def wrapped_runner(*args, catch_errors=False):
        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
            try:
                f(list(args))
            except BaseException as exc:
                if not catch_errors:
                    raise
                elif isinstance(catch_errors, BaseException) and not isinstance(exc, catch_errors):
                    raise
                return stdout.getvalue(), stderr.getvalue(), exc
        return stdout.getvalue(), stderr.getvalue()

    return wrapped_runner


@runner
def runner_entrypoint(args):
    """ Run bonobo using the python command entrypoint directly (bonobo.commands.entrypoint). """
    return entrypoint(args)


@runner
def runner_module(args):
    """ Run bonobo using the bonobo.__main__ file, which is equivalent as doing "python -m bonobo ..."."""
    with patch.object(sys, 'argv', ['bonobo', *args]):
        return runpy.run_path(__main__.__file__, run_name='__main__')


all_runners = pytest.mark.parametrize('runner', [runner_entrypoint, runner_module])


def test_entrypoint():
    commands = {}

    for command in pkg_resources.iter_entry_points('bonobo.commands'):
        commands[command.name] = command

    assert not {
        'convert',
        'init',
        'inspect',
        'run',
        'version',
    }.difference(set(commands))


@all_runners
def test_no_command(runner):
    _, err, exc = runner(catch_errors=True)
    assert type(exc) == SystemExit
    assert 'error: the following arguments are required: command' in err


@all_runners
def test_run(runner):
    out, err = runner('run', '--quiet', get_examples_path('types/strings.py'))
    out = out.split('\n')
    assert out[0].startswith('Foo ')
    assert out[1].startswith('Bar ')
    assert out[2].startswith('Baz ')


@all_runners
def test_run_module(runner):
    out, err = runner('run', '--quiet', '-m', 'bonobo.examples.types.strings')
    out = out.split('\n')
    assert out[0].startswith('Foo ')
    assert out[1].startswith('Bar ')
    assert out[2].startswith('Baz ')


@all_runners
def test_run_path(runner):
    out, err = runner('run', '--quiet', get_examples_path('types'))
    out = out.split('\n')
    assert out[0].startswith('Foo ')
    assert out[1].startswith('Bar ')
    assert out[2].startswith('Baz ')


@all_runners
def test_install_requirements_for_dir(runner):
    dirname = get_examples_path('types')
    with patch('bonobo.commands.run._install_requirements') as install_mock:
        runner('run', '--install', dirname)
    install_mock.assert_called_once_with(os.path.join(dirname, 'requirements.txt'))


@all_runners
def test_install_requirements_for_file(runner):
    dirname = get_examples_path('types')
    with patch('bonobo.commands.run._install_requirements') as install_mock:
        runner('run', '--install', os.path.join(dirname, 'strings.py'))
    install_mock.assert_called_once_with(os.path.join(dirname, 'requirements.txt'))


@all_runners
def test_version(runner):
    out, err = runner('version')
    out = out.strip()
    assert out.startswith('bonobo ')
    assert __version__ in out

    out, err = runner('version', '-q')
    out = out.strip()
    assert out.startswith('bonobo ')
    assert __version__ in out

    out, err = runner('version', '-qq')
    out = out.strip()
    assert not out.startswith('bonobo ')
    assert __version__ in out


@all_runners
def test_download_works_for_examples(runner):
    expected_bytes = b'hello world'

    class MockResponse(object):
        def __init__(self):
            self.status_code = 200

        def iter_content(self, *args, **kwargs):
            return [expected_bytes]

        def __enter__(self):
            return self

        def __exit__(self, *args, **kwargs):
            pass

    fout = io.BytesIO()
    fout.close = lambda: None

    with patch('bonobo.commands.download._open_url') as mock_open_url, \
            patch('bonobo.commands.download.open') as mock_open:
        mock_open_url.return_value = MockResponse()
        mock_open.return_value = fout
        runner('download', 'examples/datasets/coffeeshops.txt')
    expected_url = EXAMPLES_BASE_URL + 'datasets/coffeeshops.txt'
    mock_open_url.assert_called_once_with(expected_url)

    assert fout.getvalue() == expected_bytes


@all_runners
def test_download_fails_non_example(runner):
    with pytest.raises(ValueError):
        runner('download', '/something/entirely/different.txt')


@pytest.fixture
def env1(tmpdir):
    env_file = tmpdir.join('.env_one')
    env_file.write('\n'.join((
        'SECRET=unknown',
        'PASSWORD=sweet',
        'PATH=first',
    )))
    return str(env_file)


@pytest.fixture
def env2(tmpdir):
    env_file = tmpdir.join('.env_two')
    env_file.write('\n'.join((
        'PASSWORD=bitter',
        "PATH='second'",
    )))
    return str(env_file)


all_environ_targets = pytest.mark.parametrize(
    'target', [
        (get_examples_path('environ.py'), ),
        (
            '-m',
            'bonobo.examples.environ',
        ),
    ]
)


@all_runners
@all_environ_targets
class EnvironmentTestCase():
    def run_quiet(self, runner, *args):
        return runner('run', '--quiet', *args)

    def run_environ(self, runner, *args, environ=None):
        _environ = {'PATH': '/usr/bin'}
        if environ:
            _environ.update(environ)

        with patch.dict('os.environ', _environ, clear=True):
            out, err = self.run_quiet(runner, *args)
            assert 'SECRET' not in os.environ
            assert 'PASSWORD' not in os.environ
            if 'PATH' in _environ:
                assert 'PATH' in os.environ
                assert os.environ['PATH'] == _environ['PATH']

        assert err == ''
        return dict(map(lambda line: line.split(' ', 1), filter(None, out.split('\n'))))


class TestDefaultEnvFile(EnvironmentTestCase):
    def test_run_with_default_env_file(self, runner, target, env1):
        env = self.run_environ(runner, *target, '--default-env-file', env1)
        assert env.get('SECRET') == 'unknown'
        assert env.get('PASSWORD') == 'sweet'
        assert env.get('PATH') == '/usr/bin'

    def test_run_with_multiple_default_env_files(self, runner, target, env1, env2):
        env = self.run_environ(runner, *target, '--default-env-file', env1, '--default-env-file', env2)
        assert env.get('SECRET') == 'unknown'
        assert env.get('PASSWORD') == 'sweet'
        assert env.get('PATH') == '/usr/bin'

        env = self.run_environ(runner, *target, '--default-env-file', env2, '--default-env-file', env1)
        assert env.get('SECRET') == 'unknown'
        assert env.get('PASSWORD') == 'bitter'
        assert env.get('PATH') == '/usr/bin'


class TestEnvFile(EnvironmentTestCase):
    def test_run_with_file(self, runner, target, env1):
        env = self.run_environ(runner, *target, '--env-file', env1)
        assert env.get('SECRET') == 'unknown'
        assert env.get('PASSWORD') == 'sweet'
        assert env.get('PATH') == 'first'

    def test_run_with_multiple_files(self, runner, target, env1, env2):
        env = self.run_environ(runner, *target, '--env-file', env1, '--env-file', env2)
        assert env.get('SECRET') == 'unknown'
        assert env.get('PASSWORD') == 'bitter'
        assert env.get('PATH') == 'second'

        env = self.run_environ(runner, *target, '--env-file', env2, '--env-file', env1)
        assert env.get('SECRET') == 'unknown'
        assert env.get('PASSWORD') == 'sweet'
        assert env.get('PATH') == 'first'


class TestEnvFileCombinations(EnvironmentTestCase):
    def test_run_with_both_env_files(self, runner, target, env1, env2):
        env = self.run_environ(runner, *target, '--default-env-file', env1, '--env-file', env2)
        assert env.get('SECRET') == 'unknown'
        assert env.get('PASSWORD') == 'bitter'
        assert env.get('PATH') == 'second'

    def test_run_with_both_env_files_then_overrides(self, runner, target, env1, env2):
        env = self.run_environ(
            runner, *target, '--default-env-file', env1, '--env-file', env2, '--env', 'PASSWORD=mine', '--env',
            'SECRET=s3cr3t'
        )
        assert env.get('SECRET') == 's3cr3t'
        assert env.get('PASSWORD') == 'mine'
        assert env.get('PATH') == 'second'


class TestEnvVars(EnvironmentTestCase):
    def test_run_no_env(self, runner, target):
        env = self.run_environ(runner, *target, environ={'USER': 'romain'})
        assert env.get('USER') == 'romain'

    def test_run_env(self, runner, target):
        env = self.run_environ(runner, *target, '--env', 'USER=serious', environ={'USER': 'romain'})
        assert env.get('USER') == 'serious'

    def test_run_env_mixed(self, runner, target):
        env = self.run_environ(runner, *target, '--env', 'ONE=1', '--env', 'TWO="2"', environ={'USER': 'romain'})
        assert env.get('USER') == 'romain'
        assert env.get('ONE') == '1'
        assert env.get('TWO') == '2'

    def test_run_default_env(self, runner, target):
        env = self.run_environ(runner, *target, '--default-env', 'USER=clown')
        assert env.get('USER') == 'clown'

        env = self.run_environ(runner, *target, '--default-env', 'USER=clown', environ={'USER': 'romain'})
        assert env.get('USER') == 'romain'

        env = self.run_environ(
            runner, *target, '--env', 'USER=serious', '--default-env', 'USER=clown', environ={
                'USER': 'romain'
            }
        )
        assert env.get('USER') == 'serious'
