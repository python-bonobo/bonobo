import pytest

from bonobo import Bag, JsonFileWriter
from bonobo.core.contexts import ComponentExecutionContext
from bonobo.util.tokens import BEGIN, END


def test_write_json_to_file(tmpdir):
    file = tmpdir.join('output.json')
    json_writer = JsonFileWriter(str(file))
    context = ComponentExecutionContext(json_writer, None)

    context.initialize()
    context.recv(BEGIN, Bag({'foo': 'bar'}), END)
    context.step()
    context.finalize()

    assert file.read() == '''[
{"foo": "bar"}
]'''

    with pytest.raises(AttributeError):
        getattr(context, 'fp')

    with pytest.raises(AttributeError):
        getattr(context, 'first')


def test_write_json_without_initializer_should_not_work(tmpdir):
    file = tmpdir.join('output.json')
    json_writer = JsonFileWriter(str(file))

    context = ComponentExecutionContext(json_writer, None)
    with pytest.raises(AttributeError):
        json_writer(context, {'foo': 'bar'})
