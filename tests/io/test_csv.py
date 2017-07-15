import pytest

from bonobo import Bag, CsvReader, CsvWriter, settings
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext, FilesystemTester

csv_tester = FilesystemTester('csv')
csv_tester.input_data = 'a,b,c\na foo,b foo,c foo\na bar,b bar,c bar'


def test_write_csv_to_file_arg0(tmpdir):
    fs, filename, services = csv_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(CsvWriter(path=filename, ioformat=settings.IOFORMAT_ARG0), services=services) as context:
        context.write(BEGIN, Bag({'foo': 'bar'}), Bag({'foo': 'baz', 'ignore': 'this'}), END)
        context.step()
        context.step()

    with fs.open(filename) as fp:
        assert fp.read() == 'foo\nbar\nbaz\n'

    with pytest.raises(AttributeError):
        getattr(context, 'file')


@pytest.mark.parametrize('add_kwargs', ({}, {
    'ioformat': settings.IOFORMAT_KWARGS,
}, ))
def test_write_csv_to_file_kwargs(tmpdir, add_kwargs):
    fs, filename, services = csv_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(CsvWriter(path=filename, **add_kwargs), services=services) as context:
        context.write(BEGIN, Bag(**{'foo': 'bar'}), Bag(**{'foo': 'baz', 'ignore': 'this'}), END)
        context.step()
        context.step()

    with fs.open(filename) as fp:
        assert fp.read() == 'foo\nbar\nbaz\n'

    with pytest.raises(AttributeError):
        getattr(context, 'file')


def test_read_csv_from_file_arg0(tmpdir):
    fs, filename, services = csv_tester.get_services_for_reader(tmpdir)

    with CapturingNodeExecutionContext(
        CsvReader(path=filename, delimiter=',', ioformat=settings.IOFORMAT_ARG0),
        services=services,
    ) as context:
        context.write(BEGIN, Bag(), END)
        context.step()

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


def test_read_csv_from_file_kwargs(tmpdir):
    fs, filename, services = csv_tester.get_services_for_reader(tmpdir)

    with CapturingNodeExecutionContext(
        CsvReader(path=filename, delimiter=','),
        services=services,
    ) as context:
        context.write(BEGIN, Bag(), END)
        context.step()

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
