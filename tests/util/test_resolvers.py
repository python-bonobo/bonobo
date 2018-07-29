import bonobo
from bonobo.util.resolvers import _parse_option, _resolve_options, _resolve_transformations


def test_parse_option():
    assert _parse_option("foo=bar") == ("foo", "bar")
    assert _parse_option('foo="bar"') == ("foo", "bar")
    assert _parse_option('sep=";"') == ("sep", ";")
    assert _parse_option("foo") == ("foo", True)


def test_resolve_options():
    assert _resolve_options(("foo=bar", 'bar="baz"')) == {"foo": "bar", "bar": "baz"}
    assert _resolve_options() == {}


def test_resolve_transformations():
    assert _resolve_transformations(("PrettyPrinter",)) == (bonobo.PrettyPrinter,)
