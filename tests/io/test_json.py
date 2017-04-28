import pytest

from bonobo import Bag, JsonReader, JsonWriter, open_fs
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext


def test_write_json_to_file(tmpdir):
    fs, filename = open_fs(tmpdir), 'output.json'

    writer = JsonWriter(path=filename)
    context = NodeExecutionContext(writer, services={'fs': fs})

    context.start()
    context.recv(BEGIN, Bag({'foo': 'bar'}), END)
    context.step()
    context.stop()

    assert fs.open(filename).read() == '[\n{"foo": "bar"}\n]'

    with pytest.raises(AttributeError):
        getattr(context, 'file')

    with pytest.raises(AttributeError):
        getattr(context, 'first')


def test_read_json_from_file(tmpdir):
    fs, filename = open_fs(tmpdir), 'input.json'
    fs.open(filename, 'w').write('[{"x": "foo"},{"x": "bar"}]')
    reader = JsonReader(path=filename)

    context = CapturingNodeExecutionContext(reader, services={'fs': fs})

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
