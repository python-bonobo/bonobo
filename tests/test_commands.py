import os
import runpy
import sys
from unittest.mock import patch

import pkg_resources
import pytest

from bonobo import __main__, __version__, get_examples_path
from bonobo.commands import entrypoint


def runner_entrypoint(*args):
    """ Run bonobo using the python command entrypoint directly (bonobo.commands.entrypoint). """
    return entrypoint(list(args))


def runner_module(*args):
    """ Run bonobo using the bonobo.__main__ file, which is equivalent as doing "python -m bonobo ..."."""
    with patch.object(sys, 'argv', ['bonobo', *args]):
        return runpy.run_path(__main__.__file__, run_name='__main__')


all_runners = pytest.mark.parametrize('runner', [runner_entrypoint, runner_module])


def test_entrypoint():
    commands = {}

    for command in pkg_resources.iter_entry_points('bonobo.commands'):
        commands[command.name] = command

    assert 'init' in commands
    assert 'run' in commands
    assert 'version' in commands


@all_runners
def test_no_command(runner, capsys):
    with pytest.raises(SystemExit):
        runner()
    _, err = capsys.readouterr()
    assert 'error: the following arguments are required: command' in err


@all_runners
def test_run(runner, capsys):
    runner('run', '--quiet', get_examples_path('types/strings.py'))
    out, err = capsys.readouterr()
    out = out.split('\n')
    assert out[0].startswith('Foo ')
    assert out[1].startswith('Bar ')
    assert out[2].startswith('Baz ')


@all_runners
def test_run_module(runner, capsys):
    runner('run', '--quiet', '-m', 'bonobo.examples.types.strings')
    out, err = capsys.readouterr()
    out = out.split('\n')
    assert out[0].startswith('Foo ')
    assert out[1].startswith('Bar ')
    assert out[2].startswith('Baz ')


@all_runners
def test_run_path(runner, capsys):
    runner('run', '--quiet', get_examples_path('types'))
    out, err = capsys.readouterr()
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
def test_version(runner, capsys):
    runner('version')
    out, err = capsys.readouterr()
    out = out.strip()
    assert out.startswith('bonobo ')
    assert __version__ in out


@all_runners
class TestDefaultEnvFile(object):
    def test_run_file_with_default_env_file(self, runner, capsys):
        runner(
            'run', '--quiet', '--default-env-file', '.env_one',
            get_examples_path('environment/env_files/get_passed_env_file.py')
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] != 'marzo'

    def test_run_file_with_multiple_default_env_files(self, runner, capsys):
        runner(
            'run', '--quiet', '--default-env-file', '.env_one',
            '--default-env-file', '.env_two',
            get_examples_path('environment/env_files/get_passed_env_file.py')
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] != 'marzo'

    def test_run_module_with_default_env_file(self, runner, capsys):
        runner(
            'run', '--quiet', '-m',
            'bonobo.examples.environment.env_files.get_passed_env_file',
            '--default-env-file', '.env_one'
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] != 'marzo'

    def test_run_module_with_multiple_default_env_files(self, runner, capsys):
        runner(
            'run', '--quiet', '-m',
            'bonobo.examples.environment.env_files.get_passed_env_file',
            '--default-env-file', '.env_one', '--default-env-file', '.env_two',
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] != 'marzo'


@all_runners
class TestEnvFile(object):
    def test_run_file_with_file(self, runner, capsys):
        runner(
            'run', '--quiet',
            get_examples_path('environment/env_files/get_passed_env_file.py'),
            '--env-file', '.env_one',
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] == 'marzo'

    def test_run_file_with_multiple_files(self, runner, capsys):
        runner(
            'run', '--quiet',
            get_examples_path('environment/env_files/get_passed_env_file.py'),
            '--env-file', '.env_one', '--env-file', '.env_two',
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'not_sweet_password'
        assert out[2] == 'abril'

    def test_run_module_with_file(self, runner, capsys):
        runner(
            'run', '--quiet', '-m',
            'bonobo.examples.environment.env_files.get_passed_env_file',
            '--env-file', '.env_one',
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] == 'marzo'

    def test_run_module_with_multiple_files(self, runner, capsys):
        runner(
            'run', '--quiet', '-m',
            'bonobo.examples.environment.env_files.get_passed_env_file',
            '--env-file', '.env_one', '--env-file', '.env_two',
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'not_sweet_password'
        assert out[2] == 'abril'


@all_runners
class TestEnvFileCombinations(object):
    def test_run_file_with_default_env_file_and_env_file(self, runner, capsys):
        runner(
            'run', '--quiet',
            get_examples_path('environment/env_files/get_passed_env_file.py'),
            '--default-env-file', '.env_one', '--env-file', '.env_two',
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'not_sweet_password'
        assert out[2] == 'abril'

    def test_run_file_with_default_env_file_and_env_file_and_env_vars(self, runner, capsys):
        runner(
            'run', '--quiet',
            get_examples_path('environment/env_files/get_passed_env_file.py'),
            '--default-env-file', '.env_one', '--env-file', '.env_two',
            '--env', 'TEST_USER_PASSWORD=SWEETpassWORD', '--env',
            'MY_SECRET=444',
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == '444'
        assert out[1] == 'SWEETpassWORD'
        assert out[2] == 'abril'


@all_runners
class TestDefaultEnvVars(object):
    def test_run_file_with_default_env_var(self, runner, capsys):
        runner(
            'run', '--quiet',
            get_examples_path('environment/env_vars/get_passed_env.py'),
            '--default-env', 'USER=clowncity'
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == 'user'
        assert out[1] == 'number'
        assert out[2] == 'string'
        assert out[3] != 'clowncity'

    def test_run_file_with_default_env_vars(self, runner, capsys):
        runner(
            'run', '--quiet',
            get_examples_path('environment/env_vars/get_passed_env.py'),
            '--env', 'ENV_TEST_NUMBER=123', '--env', 'ENV_TEST_USER=cwandrews',
            '--default-env', "ENV_TEST_STRING='my_test_string'"
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'

    def test_run_module_with_default_env_var(self, runner, capsys):
        runner(
            'run', '--quiet', '-m',
            'bonobo.examples.environment.env_vars.get_passed_env',
            '--env', 'ENV_TEST_NUMBER=123',
            '--default-env', 'ENV_TEST_STRING=string'
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] != 'string'

    def test_run_module_with_default_env_vars(self, runner, capsys):
        runner(
            'run', '--quiet', '-m',
            'bonobo.examples.environment.env_vars.get_passed_env',
            '--env', 'ENV_TEST_NUMBER=123', '--env', 'ENV_TEST_USER=cwandrews',
            '--default-env', "ENV_TEST_STRING='string'"
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] != 'string'


@all_runners
class TestEnvVars(object):
    def test_run_file_with_env_var(self, runner, capsys):
        runner(
            'run', '--quiet',
            get_examples_path('environment/env_vars/get_passed_env.py'),
            '--env', 'ENV_TEST_NUMBER=123'
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] != 'test_user'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'

    def test_run_file_with_env_vars(self, runner, capsys):
        runner(
            'run', '--quiet',
            get_examples_path('environment/env_vars/get_passed_env.py'),
            '--env', 'ENV_TEST_NUMBER=123', '--env', 'ENV_TEST_USER=cwandrews',
            '--env', "ENV_TEST_STRING='my_test_string'"
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'

    def test_run_module_with_env_var(self, runner, capsys):
        runner(
            'run', '--quiet', '-m',
            'bonobo.examples.environment.env_vars.get_passed_env',
            '--env', 'ENV_TEST_NUMBER=123'
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'

    def test_run_module_with_env_vars(self, runner, capsys):
        runner(
            'run', '--quiet', '-m',
            'bonobo.examples.environment.env_vars.get_passed_env',
            '--env', 'ENV_TEST_NUMBER=123', '--env', 'ENV_TEST_USER=cwandrews',
            '--env', "ENV_TEST_STRING='my_test_string'"
        )
        out, err = capsys.readouterr()
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'
