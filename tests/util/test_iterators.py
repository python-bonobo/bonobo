import types

from bonobo.util.iterators import force_iterator


def test_force_iterator_with_string():
    assert force_iterator('foo') == ['foo']


def test_force_iterator_with_none():
    assert force_iterator(None) == []


def test_force_iterator_with_generator():
    def generator():
        yield 'aaa'
        yield 'bbb'
        yield 'ccc'

    iterator = force_iterator(generator())
    assert type(iterator) == types.GeneratorType
    assert list(iterator) == ['aaa', 'bbb', 'ccc']
