import runpy
import sys
from unittest.mock import patch

import pkg_resources
import pytest

from bonobo import __main__, __version__, get_examples_path
from bonobo.commands import entrypoint


def runner_entrypoint(*args):
    return entrypoint(list(args))


def runner_module(*args):
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
def test_version(runner, capsys):
    runner('version')
    out, err = capsys.readouterr()
    out = out.strip()
    assert out.startswith('bonobo ')
    assert __version__ in out
