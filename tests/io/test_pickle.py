import pickle
import pytest

from bonobo import Bag, PickleReader, PickleWriter, open_fs
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext


def test_write_pickled_dict_to_file(tmpdir):
    fs, filename = open_fs(tmpdir), 'output.pkl'

    writer = PickleWriter(path=filename)
    context = NodeExecutionContext(writer, services={'fs': fs})

    context.write(BEGIN, Bag({'foo': 'bar'}), Bag({'foo': 'baz', 'ignore': 'this'}), END)

    context.start()
    context.step()
    context.step()
    context.stop()

    with fs.open(filename, 'rb') as fp:
        assert pickle.loads(fp.read()) == {'foo': 'bar'}

    with pytest.raises(AttributeError):
        getattr(context, 'file')


def test_read_pickled_list_from_file(tmpdir):
    fs, filename = open_fs(tmpdir), 'input.pkl'
    with fs.open(filename, 'wb') as fp:
        fp.write(pickle.dumps([['a', 'b', 'c'], ['a foo', 'b foo', 'c foo'], ['a bar', 'b bar', 'c bar']]))

    reader = PickleReader(path=filename)

    context = CapturingNodeExecutionContext(reader, services={'fs': fs})

    context.start()
    context.write(BEGIN, Bag(), END)
    context.step()
    context.stop()

    assert len(context.send.mock_calls) == 2

    args0, kwargs0 = context.send.call_args_list[0]
    assert len(args0) == 1 and not len(kwargs0)
    args1, kwargs1 = context.send.call_args_list[1]
    assert len(args1) == 1 and not len(kwargs1)

    assert args0[0].args[0] == {
        'a': 'a foo',
        'b': 'b foo',
        'c': 'c foo',
    }
    assert args1[0].args[0] == {
        'a': 'a bar',
        'b': 'b bar',
        'c': 'c bar',
    }
