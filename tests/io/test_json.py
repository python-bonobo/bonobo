import pytest

from bonobo import to_json
from bonobo.util.lifecycle import get_initializer, get_finalizer


class ContextMock:
    pass


def test_write_json_to_file(tmpdir):
    file = tmpdir.join('output.json')
    json_writer = to_json(str(file))
    context = ContextMock()

    get_initializer(json_writer)(context)
    json_writer(context, {'foo': 'bar'})
    get_finalizer(json_writer)(context)

    assert file.read() == '''[
{"foo": "bar"}
]'''

    with pytest.raises(AttributeError):
        getattr(context, 'fp')

    with pytest.raises(AttributeError):
        getattr(context, 'first')


def test_write_json_without_initializer_should_not_work(tmpdir):
    file = tmpdir.join('output.json')
    json_writer = to_json(str(file))

    context = ContextMock()
    with pytest.raises(AttributeError):
        json_writer(context, {'foo': 'bar'})
