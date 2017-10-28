import functools
import io
import os
import runpy
import sys
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch, Mock

import pkg_resources
import pytest
from cookiecutter.exceptions import OutputDirExistsException

from bonobo import __main__, __version__, get_examples_path
from bonobo.commands import entrypoint
from bonobo.commands.run import DEFAULT_GRAPH_FILENAMES
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
single_runner = pytest.mark.parametrize('runner', [runner_module])


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
def test_init(runner, tmpdir):
    name = 'project'
    tmpdir.chdir()
    runner('init', name)
    assert os.path.isdir(name)
    assert set(os.listdir(name)) & set(DEFAULT_GRAPH_FILENAMES)

@single_runner
def test_init_in_empty_then_nonempty_directory(runner, tmpdir):
    name = 'project'
    tmpdir.chdir()
    os.mkdir(name)

    # run in empty dir
    runner('init', name)
    assert set(os.listdir(name)) & set(DEFAULT_GRAPH_FILENAMES)

    # run in non empty dir
    with pytest.raises(OutputDirExistsException):
        runner('init', name)


@single_runner
def test_init_within_empty_directory(runner, tmpdir):
    tmpdir.chdir()
    runner('init', '.')
    assert set(os.listdir()) & set(DEFAULT_GRAPH_FILENAMES)


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


@all_runners
def test_download_works_for_examples(runner):
    expected_bytes = b'hello world'

    class MockResponse(object):
        def __init__(self):
            self.status_code = 200

        def iter_content(self, *args, **kwargs):
            return [expected_bytes]

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


@all_runners
class TestDefaultEnvFile(object):
    def test_run_file_with_default_env_file(self, runner):
        out, err = runner(
            'run', '--quiet', '--default-env-file', '.env_one',
            get_examples_path('environment/env_files/get_passed_env_file.py')
        )
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] != 'marzo'

    def test_run_file_with_multiple_default_env_files(self, runner):
        out, err = runner(
            'run', '--quiet', '--default-env-file', '.env_one', '--default-env-file', '.env_two',
            get_examples_path('environment/env_files/get_passed_env_file.py')
        )
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] != 'marzo'

    def test_run_module_with_default_env_file(self, runner):
        out, err = runner(
            'run', '--quiet', '-m', 'bonobo.examples.environment.env_files.get_passed_env_file', '--default-env-file',
            '.env_one'
        )
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] != 'marzo'

    def test_run_module_with_multiple_default_env_files(self, runner):
        out, err = runner(
            'run',
            '--quiet',
            '-m',
            'bonobo.examples.environment.env_files.get_passed_env_file',
            '--default-env-file',
            '.env_one',
            '--default-env-file',
            '.env_two',
        )
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] != 'marzo'


@all_runners
class TestEnvFile(object):
    def test_run_file_with_file(self, runner):
        out, err = runner(
            'run',
            '--quiet',
            get_examples_path('environment/env_files/get_passed_env_file.py'),
            '--env-file',
            '.env_one',
        )
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] == 'marzo'

    def test_run_file_with_multiple_files(self, runner):
        out, err = runner(
            'run',
            '--quiet',
            get_examples_path('environment/env_files/get_passed_env_file.py'),
            '--env-file',
            '.env_one',
            '--env-file',
            '.env_two',
        )
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'not_sweet_password'
        assert out[2] == 'abril'

    def test_run_module_with_file(self, runner):
        out, err = runner(
            'run',
            '--quiet',
            '-m',
            'bonobo.examples.environment.env_files.get_passed_env_file',
            '--env-file',
            '.env_one',
        )
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'sweetpassword'
        assert out[2] == 'marzo'

    def test_run_module_with_multiple_files(self, runner):
        out, err = runner(
            'run',
            '--quiet',
            '-m',
            'bonobo.examples.environment.env_files.get_passed_env_file',
            '--env-file',
            '.env_one',
            '--env-file',
            '.env_two',
        )
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'not_sweet_password'
        assert out[2] == 'abril'


@all_runners
class TestEnvFileCombinations:
    def test_run_file_with_default_env_file_and_env_file(self, runner):
        out, err = runner(
            'run',
            '--quiet',
            get_examples_path('environment/env_files/get_passed_env_file.py'),
            '--default-env-file',
            '.env_one',
            '--env-file',
            '.env_two',
        )
        out = out.split('\n')
        assert out[0] == '321'
        assert out[1] == 'not_sweet_password'
        assert out[2] == 'abril'

    def test_run_file_with_default_env_file_and_env_file_and_env_vars(self, runner):
        out, err = runner(
            'run',
            '--quiet',
            get_examples_path('environment/env_files/get_passed_env_file.py'),
            '--default-env-file',
            '.env_one',
            '--env-file',
            '.env_two',
            '--env',
            'TEST_USER_PASSWORD=SWEETpassWORD',
            '--env',
            'MY_SECRET=444',
        )
        out = out.split('\n')
        assert out[0] == '444'
        assert out[1] == 'SWEETpassWORD'
        assert out[2] == 'abril'


@all_runners
class TestDefaultEnvVars:
    def test_run_file_with_default_env_var(self, runner):
        out, err = runner(
            'run', '--quiet',
            get_examples_path('environment/env_vars/get_passed_env.py'), '--default-env', 'USER=clowncity', '--env',
            'USER=ted'
        )
        out = out.split('\n')
        assert out[0] == 'user'
        assert out[1] == 'number'
        assert out[2] == 'string'
        assert out[3] != 'clowncity'

    def test_run_file_with_default_env_vars(self, runner):
        out, err = runner(
            'run', '--quiet',
            get_examples_path('environment/env_vars/get_passed_env.py'), '--env', 'ENV_TEST_NUMBER=123', '--env',
            'ENV_TEST_USER=cwandrews', '--default-env', "ENV_TEST_STRING='my_test_string'"
        )
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'

    def test_run_module_with_default_env_var(self, runner):
        out, err = runner(
            'run', '--quiet', '-m', 'bonobo.examples.environment.env_vars.get_passed_env', '--env',
            'ENV_TEST_NUMBER=123', '--default-env', 'ENV_TEST_STRING=string'
        )
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] != 'string'

    def test_run_module_with_default_env_vars(self, runner):
        out, err = runner(
            'run', '--quiet', '-m', 'bonobo.examples.environment.env_vars.get_passed_env', '--env',
            'ENV_TEST_NUMBER=123', '--env', 'ENV_TEST_USER=cwandrews', '--default-env', "ENV_TEST_STRING='string'"
        )
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] != 'string'


@all_runners
class TestEnvVars:
    def test_run_file_with_env_var(self, runner):
        out, err = runner(
            'run', '--quiet',
            get_examples_path('environment/env_vars/get_passed_env.py'), '--env', 'ENV_TEST_NUMBER=123'
        )
        out = out.split('\n')
        assert out[0] != 'test_user'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'

    def test_run_file_with_env_vars(self, runner):
        out, err = runner(
            'run', '--quiet',
            get_examples_path('environment/env_vars/get_passed_env.py'), '--env', 'ENV_TEST_NUMBER=123', '--env',
            'ENV_TEST_USER=cwandrews', '--env', "ENV_TEST_STRING='my_test_string'"
        )
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'

    def test_run_module_with_env_var(self, runner):
        out, err = runner(
            'run', '--quiet', '-m', 'bonobo.examples.environment.env_vars.get_passed_env', '--env',
            'ENV_TEST_NUMBER=123'
        )
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'

    def test_run_module_with_env_vars(self, runner):
        out, err = runner(
            'run', '--quiet', '-m', 'bonobo.examples.environment.env_vars.get_passed_env', '--env',
            'ENV_TEST_NUMBER=123', '--env', 'ENV_TEST_USER=cwandrews', '--env', "ENV_TEST_STRING='my_test_string'"
        )
        out = out.split('\n')
        assert out[0] == 'cwandrews'
        assert out[1] == '123'
        assert out[2] == 'my_test_string'
