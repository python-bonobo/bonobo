import os

import pytest

from bonobo.commands.init import InitCommand
from bonobo.util.testing import all_runners


@all_runners
def test_init_file(runner, tmpdir):
    target = tmpdir.join("foo.py")
    target_filename = str(target)
    runner("init", target_filename)
    assert os.path.exists(target_filename)

    out, err = runner("run", target_filename)
    assert out.replace("\n", " ").strip() == "Hello World"
    assert not err


@all_runners
@pytest.mark.parametrize("template", InitCommand.TEMPLATES)
def test_init_file_templates(runner, template, tmpdir):
    target = tmpdir.join("foo.py")
    target_filename = str(target)
    runner("init", target_filename)
    assert os.path.exists(target_filename)
    out, err = runner("run", target_filename)
    assert not err
