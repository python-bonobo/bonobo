from bonobo import __version__
from bonobo.util.testing import all_runners


@all_runners
def test_version(runner):
    out, err = runner("version")
    out = out.strip()
    assert out.startswith("bonobo ")
    assert __version__ in out

    out, err = runner("version", "-q")
    out = out.strip()
    assert out.startswith("bonobo ")
    assert __version__ in out

    out, err = runner("version", "-qq")
    out = out.strip()
    assert not out.startswith("bonobo ")
    assert __version__ in out
