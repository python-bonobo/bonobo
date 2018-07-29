import pkg_resources

from bonobo.util.testing import all_runners


def test_entrypoint():
    commands = {}

    for command in pkg_resources.iter_entry_points("bonobo.commands"):
        commands[command.name] = command

    assert not {"convert", "init", "inspect", "run", "version"}.difference(set(commands))


@all_runners
def test_no_command(runner):
    _, err, exc = runner(catch_errors=True)
    assert type(exc) == SystemExit
    assert "error: the following arguments are required: command" in err
