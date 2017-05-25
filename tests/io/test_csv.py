import pytest

from bonobo import Bag, CsvReader, CsvWriter, open_fs
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext


def test_write_csv_to_file(tmpdir):
    fs, filename = open_fs(tmpdir), 'output.csv'

    writer = CsvWriter(path=filename)
    context = NodeExecutionContext(writer, services={'fs': fs})

    context.write(BEGIN, Bag({'foo': 'bar'}), Bag({'foo': 'baz', 'ignore': 'this'}), END)

    context.start()
    context.step()
    context.step()
    context.stop()

    assert fs.open(filename).read() == 'foo\nbar\nbaz\n'

    with pytest.raises(AttributeError):
        getattr(context, 'file')


def test_read_csv_from_file(tmpdir):
    fs, filename = open_fs(tmpdir), 'input.csv'
    fs.open(filename, 'w').write('a,b,c\na foo,b foo,c foo\na bar,b bar,c bar')

    reader = CsvReader(path=filename, delimiter=',')

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


def test_read_csv_kwargs_output_formater(tmpdir):
    fs, filename = open_fs(tmpdir), 'input.csv'
    fs.open(filename, 'w').write('a,b,c\na foo,b foo,c foo\na bar,b bar,c bar')

    reader = CsvReader(path=filename, delimiter=',', output_format='kwargs')

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

    _args, _kwargs = args0[0].get()
    assert not len(_args) and _kwargs == {
        'a': 'a foo',
        'b': 'b foo',
        'c': 'c foo',
    }

    _args, _kwargs = args1[0].get()
    assert not len(_args) and _kwargs == {
        'a': 'a bar',
        'b': 'b bar',
        'c': 'c bar',
    }
