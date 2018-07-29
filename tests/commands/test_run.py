import os
from unittest.mock import patch

from bonobo import get_examples_path
from bonobo.util.testing import all_runners


@all_runners
def test_run(runner):
    out, err = runner("run", "--quiet", get_examples_path("types/strings.py"))
    out = out.split("\n")
    assert out[0].startswith("Foo ")
    assert out[1].startswith("Bar ")
    assert out[2].startswith("Baz ")


@all_runners
def test_run_module(runner):
    out, err = runner("run", "--quiet", "-m", "bonobo.examples.types.strings")
    out = out.split("\n")
    assert out[0].startswith("Foo ")
    assert out[1].startswith("Bar ")
    assert out[2].startswith("Baz ")


@all_runners
def test_run_path(runner):
    out, err = runner("run", "--quiet", get_examples_path("types"))
    out = out.split("\n")
    assert out[0].startswith("Foo ")
    assert out[1].startswith("Bar ")
    assert out[2].startswith("Baz ")


@all_runners
def test_install_requirements_for_dir(runner):
    dirname = get_examples_path("types")
    with patch("bonobo.commands.run._install_requirements") as install_mock:
        runner("run", "--install", dirname)
    install_mock.assert_called_once_with(os.path.join(dirname, "requirements.txt"))


@all_runners
def test_install_requirements_for_file(runner):
    dirname = get_examples_path("types")
    with patch("bonobo.commands.run._install_requirements") as install_mock:
        runner("run", "--install", os.path.join(dirname, "strings.py"))
    install_mock.assert_called_once_with(os.path.join(dirname, "requirements.txt"))
