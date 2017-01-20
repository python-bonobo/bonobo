import pkg_resources
import pytest

from bonobo import get_examples_path
from bonobo.commands import entrypoint


def test_entrypoint():
    commands = {}

    for command in pkg_resources.iter_entry_points('bonobo.commands'):
        commands[command.name] = command

    assert 'init' in commands
    assert 'run' in commands

def test_no_command(capsys):
    with pytest.raises(SystemExit):
        entrypoint([])
    out, err = capsys.readouterr()
    assert 'error: the following arguments are required: command' in err

def test_init():
    pass # need ext dir

def test_run(capsys):
    entrypoint(['run', '--quiet', get_examples_path('types/strings.py')])
    out, err = capsys.readouterr()
    out = out.split('\n')
    assert out[0].startswith('Foo ')
    assert out[1].startswith('Bar ')
    assert out[2].startswith('Baz ')
