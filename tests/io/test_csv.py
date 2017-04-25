import pytest

from bonobo import Bag, CsvReader, CsvWriter
from bonobo.constants import BEGIN, END
from bonobo.execution import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext


def test_write_csv_to_file(tmpdir):
    file = tmpdir.join('output.json')
    writer = CsvWriter(path=str(file))
    context = NodeExecutionContext(writer, None)

    context.recv(BEGIN, Bag({'foo': 'bar'}), Bag({'foo': 'baz', 'ignore': 'this'}), END)

    context.start()
    context.step()
    context.step()
    context.stop()

    assert file.read() == 'foo\nbar\nbaz\n'

    with pytest.raises(AttributeError):
        getattr(context, 'file')


def test_read_csv_from_file(tmpdir):
    file = tmpdir.join('input.csv')
    file.write('a,b,c\na foo,b foo,c foo\na bar,b bar,c bar')

    reader = CsvReader(path=str(file), delimiter=',')

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
