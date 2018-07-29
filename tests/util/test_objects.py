import operator

import pytest

from bonobo.util.objects import ValueHolder, Wrapper, get_attribute_or_create, get_name
from bonobo.util.testing import optional_contextmanager


class foo:
    pass


class bar:
    __name__ = "baz"


def test_get_name():
    assert get_name(42) == "int"
    assert get_name("eat at joe.") == "str"
    assert get_name(str) == "str"
    assert get_name(object) == "object"
    assert get_name(get_name) == "get_name"
    assert get_name(foo) == "foo"
    assert get_name(foo()) == "foo"
    assert get_name(bar) == "bar"
    assert get_name(bar()) == "baz"


def test_wrapper_name():
    assert get_name(Wrapper(42)) == "int"
    assert get_name(Wrapper("eat at joe.")) == "str"
    assert get_name(Wrapper(str)) == "str"
    assert get_name(Wrapper(object)) == "object"
    assert get_name(Wrapper(foo)) == "foo"
    assert get_name(Wrapper(foo())) == "foo"
    assert get_name(Wrapper(bar)) == "bar"
    assert get_name(Wrapper(bar())) == "baz"
    assert get_name(Wrapper(get_name)) == "get_name"


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


def test_valueholder_notequal():
    x = ValueHolder(42)
    assert x != 41
    assert not (x != 42)


@pytest.mark.parametrize("rlo,rhi", [(1, 2), ("a", "b")])
def test_valueholder_ordering(rlo, rhi):
    vlo, vhi = ValueHolder(rlo), ValueHolder(rhi)

    for lo in (rlo, vlo):
        for hi in (rhi, vhi):
            assert lo < hi
            assert hi > lo
            assert lo <= lo
            assert not (lo < lo)
            assert lo >= lo


def test_valueholder_negpos():
    neg, zero, pos = ValueHolder(-1), ValueHolder(0), ValueHolder(1)

    assert -neg == pos
    assert -pos == neg
    assert -zero == zero
    assert +pos == pos
    assert +neg == neg


def test_valueholders_containers():
    x = ValueHolder({1, 2, 3, 5, 8, 13})

    assert 5 in x
    assert 42 not in x

    y = ValueHolder({"foo": "bar", "corp": "acme"})

    assert "foo" in y
    assert y["foo"] == "bar"
    with pytest.raises(KeyError):
        y["no"]
    y["no"] = "oh, wait"
    assert "no" in y
    assert "oh, wait" == y["no"]


def test_get_attribute_or_create():
    class X:
        pass

    x = X()

    with pytest.raises(AttributeError):
        x.foo

    foo = get_attribute_or_create(x, "foo", "bar")
    assert foo == "bar"
    assert x.foo == "bar"

    foo = get_attribute_or_create(x, "foo", "baz")
    assert foo == "bar"
    assert x.foo == "bar"


unsupported_operations = {
    int: {operator.matmul},
    str: {
        operator.sub,
        operator.mul,
        operator.matmul,
        operator.floordiv,
        operator.truediv,
        operator.mod,
        divmod,
        operator.pow,
        operator.lshift,
        operator.rshift,
        operator.and_,
        operator.xor,
        operator.or_,
    },
}


@pytest.mark.parametrize("x,y", [(5, 3), (0, 10), (0, 0), (1, 1), ("foo", "bar"), ("", "baz!")])
@pytest.mark.parametrize(
    "operation,inplace_operation",
    [
        (operator.add, operator.iadd),
        (operator.sub, operator.isub),
        (operator.mul, operator.imul),
        (operator.matmul, operator.imatmul),
        (operator.truediv, operator.itruediv),
        (operator.floordiv, operator.ifloordiv),
        (operator.mod, operator.imod),
        (divmod, None),
        (operator.pow, operator.ipow),
        (operator.lshift, operator.ilshift),
        (operator.rshift, operator.irshift),
        (operator.and_, operator.iand),
        (operator.xor, operator.ixor),
        (operator.or_, operator.ior),
    ],
)
def test_valueholder_integer_operations(x, y, operation, inplace_operation):
    v = ValueHolder(x)

    is_supported = operation not in unsupported_operations.get(type(x), set())

    isdiv = ("div" in operation.__name__) or ("mod" in operation.__name__)

    # forward...
    with optional_contextmanager(pytest.raises(TypeError), ignore=is_supported):
        with optional_contextmanager(pytest.raises(ZeroDivisionError), ignore=y or not isdiv):
            assert operation(x, y) == operation(v, y)

    # backward...
    with optional_contextmanager(pytest.raises(TypeError), ignore=is_supported):
        with optional_contextmanager(pytest.raises(ZeroDivisionError), ignore=x or not isdiv):
            assert operation(y, x) == operation(y, v)

    # in place...
    if inplace_operation is not None:
        with optional_contextmanager(pytest.raises(TypeError), ignore=is_supported):
            with optional_contextmanager(pytest.raises(ZeroDivisionError), ignore=y or not isdiv):
                inplace_operation(v, y)
                assert v == operation(x, y)
