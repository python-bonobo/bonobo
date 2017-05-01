from bonobo.util.objects import Wrapper, get_name, ValueHolder


class foo:
    pass


class bar:
    __name__ = 'baz'


def test_get_name():
    assert get_name(42) == 'int'
    assert get_name('eat at joe.') == 'str'
    assert get_name(str) == 'str'
    assert get_name(object) == 'object'
    assert get_name(get_name) == 'get_name'
    assert get_name(foo) == 'foo'
    assert get_name(foo()) == 'foo'
    assert get_name(bar) == 'bar'
    assert get_name(bar()) == 'baz'


def test_wrapper_name():
    assert get_name(Wrapper(42)) == 'int'
    assert get_name(Wrapper('eat at joe.')) == 'str'
    assert get_name(Wrapper(str)) == 'str'
    assert get_name(Wrapper(object)) == 'object'
    assert get_name(Wrapper(foo)) == 'foo'
    assert get_name(Wrapper(foo())) == 'foo'
    assert get_name(Wrapper(bar)) == 'bar'
    assert get_name(Wrapper(bar())) == 'baz'
    assert get_name(Wrapper(get_name)) == 'get_name'


def test_valueholder():
    x = ValueHolder(42)
    assert x == 42
    x += 1
    assert x == 43
    assert x + 1 == 44
    assert x == 43

    y = ValueHolder(44)
    assert y == 44
    y -= 1
    assert y == 43
    assert y - 1 == 42
    assert y == 43

    assert y == x
    assert y is not x
    assert repr(x) == repr(y) == repr(43)
