import operator

import pytest

from bonobo.util.objects import Wrapper, get_name, ValueHolder
from bonobo.util.testing import optional_contextmanager


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


unsupported_operations = {
    int: {operator.matmul},
    str: {
        operator.sub, operator.mul, operator.matmul, operator.floordiv, operator.truediv, operator.mod, divmod,
        operator.pow, operator.lshift, operator.rshift, operator.and_, operator.xor, operator.or_
    },
}


@pytest.mark.parametrize('x,y', [(5, 3), (0, 10), (0, 0), (1, 1), ('foo', 'bar'), ('', 'baz!')])
@pytest.mark.parametrize(
    'operation,inplace_operation', [
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
    ]
)
def test_valueholder_integer_operations(x, y, operation, inplace_operation):
    v = ValueHolder(x)

    is_supported = operation not in unsupported_operations.get(type(x), set())

    isdiv = ('div' in operation.__name__) or ('mod' in operation.__name__)

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
