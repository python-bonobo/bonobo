import pytest

from bonobo.config.configurables import Configurable
from bonobo.config.options import Option
from bonobo.util.inspect import inspect_node


class NoOptConfigurable(Configurable):
    pass


class MyConfigurable(Configurable):
    required_str = Option(str)
    default_str = Option(str, default="foo")
    integer = Option(int, required=False)


class MyHarderConfigurable(MyConfigurable):
    also_required = Option(bool, required=True)


class MyBetterConfigurable(MyConfigurable):
    required_str = Option(str, required=False, default="kaboom")


class MyConfigurableUsingPositionalOptions(MyConfigurable):
    first = Option(str, required=True, positional=True)
    second = Option(str, required=True, positional=True)
    third = Option(str, required=False, positional=True)


def test_missing_required_option_error():
    with inspect_node(MyConfigurable()) as ni:
        assert ni.partial

    with pytest.raises(TypeError) as exc:
        MyConfigurable(_final=True)
    assert exc.match("missing 1 required option:")


def test_missing_required_options_error():
    with inspect_node(MyHarderConfigurable()) as ni:
        assert ni.partial

    with pytest.raises(TypeError) as exc:
        MyHarderConfigurable(_final=True)
    assert exc.match("missing 2 required options:")


def test_extraneous_option_error():
    with pytest.raises(TypeError) as exc:
        MyConfigurable(required_str="foo", hello="world")
    assert exc.match("got 1 unexpected option:")


def test_extraneous_options_error():
    with pytest.raises(TypeError) as exc:
        MyConfigurable(required_str="foo", hello="world", acme="corp")
    assert exc.match("got 2 unexpected options:")


def test_defaults():
    o = MyConfigurable(required_str="hello")

    with inspect_node(o) as ni:
        assert not ni.partial

    assert o.required_str == "hello"
    assert o.default_str == "foo"
    assert o.integer is None


def test_str_type_factory():
    o = MyConfigurable(required_str=42)

    with inspect_node(o) as ni:
        assert not ni.partial

    assert o.required_str == "42"
    assert o.default_str == "foo"
    assert o.integer is None


def test_int_type_factory():
    o = MyConfigurable(required_str="yo", default_str="bar", integer="42")

    with inspect_node(o) as ni:
        assert not ni.partial

    assert o.required_str == "yo"
    assert o.default_str == "bar"
    assert o.integer == 42


def test_bool_type_factory():
    o = MyHarderConfigurable(required_str="yes", also_required="True")

    with inspect_node(o) as ni:
        assert not ni.partial

    assert o.required_str == "yes"
    assert o.default_str == "foo"
    assert o.integer is None
    assert o.also_required is True


def test_option_resolution_order():
    o = MyBetterConfigurable()

    with inspect_node(o) as ni:
        assert not ni.partial

    assert o.required_str == "kaboom"
    assert o.default_str == "foo"
    assert o.integer is None


def test_option_positional():
    o = MyConfigurableUsingPositionalOptions("1", "2", "3", required_str="hello")

    with inspect_node(o) as ni:
        assert not ni.partial

    assert o.first == "1"
    assert o.second == "2"
    assert o.third == "3"
    assert o.required_str == "hello"
    assert o.default_str == "foo"
    assert o.integer is None


def test_no_opt_configurable():
    o = NoOptConfigurable()

    with inspect_node(o) as ni:
        assert not ni.partial
