import pytest

from bonobo import Bag, JsonWriter, JsonReader
from bonobo.context.execution import NodeExecutionContext
from bonobo.util.objects import ValueHolder
from bonobo.util.testing import CapturingNodeExecutionContext
from bonobo.util.tokens import BEGIN, END


def test_write_json_to_file(tmpdir):
    file = tmpdir.join('output.json')
    writer = JsonWriter(path=str(file))
    context = NodeExecutionContext(writer, None)

    context.start()
    context.recv(BEGIN, Bag({'foo': 'bar'}), END)
    context.step()
    context.stop()

    assert file.read() == '[\n{"foo": "bar"}\n]'

    with pytest.raises(AttributeError):
        getattr(context, 'file')

    with pytest.raises(AttributeError):
        getattr(context, 'first')


def test_read_json_from_file(tmpdir):
    file = tmpdir.join('input.json')
    file.write('[{"x": "foo"},{"x": "bar"}]')
    reader = JsonReader(path=str(file))

    context = CapturingNodeExecutionContext(reader, None)

    context.start()
    context.recv(BEGIN, Bag(), END)
    context.step()
    context.stop()

    assert len(context.send.mock_calls) == 2

    args0, kwargs0 = context.send.call_args_list[0]
    assert len(args0) == 1 and not len(kwargs0)
    args1, kwargs1 = context.send.call_args_list[1]
    assert len(args1) == 1 and not len(kwargs1)

    assert args0[0].args[0] == {'x': 'foo'}
    assert args1[0].args[0] == {'x': 'bar'}
