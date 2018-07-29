import pytest

from bonobo.util.compat import deprecated, deprecated_alias


def test_deprecated():
    @deprecated
    def foo():
        pass

    foo = deprecated(foo)
    with pytest.warns(DeprecationWarning):
        foo()


def test_deprecated_alias():
    def foo():
        pass

    foo = deprecated_alias("bar", foo)

    with pytest.warns(DeprecationWarning):
        foo()
