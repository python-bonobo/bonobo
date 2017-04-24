from mock import Mock

from bonobo import Bag
from bonobo.constants import INHERIT_INPUT

args = ('foo', 'bar',)
kwargs = dict(acme='corp')


def test_basic():
    my_callable1 = Mock()
    my_callable2 = Mock()
    bag = Bag(*args, **kwargs)

    assert not my_callable1.called
    result1 = bag.apply(my_callable1)
    assert my_callable1.called and result1 is my_callable1.return_value

    assert not my_callable2.called
    result2 = bag.apply(my_callable2)
    assert my_callable2.called and result2 is my_callable2.return_value

    assert result1 is not result2

    my_callable1.assert_called_once_with(*args, **kwargs)
    my_callable2.assert_called_once_with(*args, **kwargs)


def test_inherit():
    bag = Bag('a', a=1)
    bag2 = Bag.inherit('b', b=2, _parent=bag)
    bag3 = bag.extend('c', c=3)
    bag4 = Bag('d', d=4)

    assert bag.args == ('a',)
    assert bag.kwargs == {'a': 1}
    assert bag.flags is ()

    assert bag2.args == ('a', 'b',)
    assert bag2.kwargs == {'a': 1, 'b': 2}
    assert INHERIT_INPUT in bag2.flags

    assert bag3.args == ('a', 'c',)
    assert bag3.kwargs == {'a': 1, 'c': 3}
    assert bag3.flags is ()

    assert bag4.args == ('d',)
    assert bag4.kwargs == {'d': 4}
    assert bag4.flags is ()

    bag4.set_parent(bag)
    assert bag4.args == ('a', 'd',)
    assert bag4.kwargs == {'a': 1, 'd': 4}
    assert bag4.flags is ()

    bag4.set_parent(bag3)
    assert bag4.args == ('a', 'c', 'd',)
    assert bag4.kwargs == {'a': 1, 'c': 3, 'd': 4}
    assert bag4.flags is ()


def test_repr():
    bag = Bag('a', a=1)
    assert repr(bag) == "<Bag ('a', a=1)>"
