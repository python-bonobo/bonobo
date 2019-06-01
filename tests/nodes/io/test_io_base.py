import pytest

from bonobo.nodes.io.base import filesystem_path


def test_filesystem_path_absolute():
    with pytest.raises(ValueError):
        filesystem_path("/this/is/absolute")


def test_filesystem_path_relative():
    assert filesystem_path("this/is/relative") == "this/is/relative"
