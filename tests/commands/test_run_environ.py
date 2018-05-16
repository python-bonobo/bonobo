import pytest

from bonobo.util.testing import EnvironmentTestCase


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
            runner, *target, '--env', 'USER=serious', '--default-env', 'USER=clown', environ={'USER': 'romain'}
        )
        assert env.get('USER') == 'serious'
