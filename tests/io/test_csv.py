import pytest

from bonobo import CsvReader, CsvWriter, settings
from bonobo.execution.contexts.node import NodeExecutionContext
from bonobo.util.testing import FilesystemTester, BufferingNodeExecutionContext

csv_tester = FilesystemTester('csv')
csv_tester.input_data = 'a,b,c\na foo,b foo,c foo\na bar,b bar,c bar'


def test_write_csv_ioformat_arg0(tmpdir):
    fs, filename, services = csv_tester.get_services_for_writer(tmpdir)
    with pytest.raises(ValueError):
        CsvWriter(path=filename, ioformat=settings.IOFORMAT_ARG0)

    with pytest.raises(ValueError):
        CsvReader(path=filename, delimiter=',', ioformat=settings.IOFORMAT_ARG0),


@pytest.mark.parametrize('add_kwargs', (
    {},
    {
        'ioformat': settings.IOFORMAT_KWARGS,
    },
))
def test_write_csv_to_file_kwargs(tmpdir, add_kwargs):
    fs, filename, services = csv_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(CsvWriter(filename, **add_kwargs), services=services) as context:
        context.write_sync({'foo': 'bar'}, {'foo': 'baz', 'ignore': 'this'})

    with fs.open(filename) as fp:
        assert fp.read() == 'foo\nbar\nbaz\n'

    with pytest.raises(AttributeError):
        getattr(context, 'file')


def test_read_csv_from_file_kwargs(tmpdir):
    fs, filename, services = csv_tester.get_services_for_reader(tmpdir)

    with BufferingNodeExecutionContext(
        CsvReader(path=filename, delimiter=','),
        services=services,
    ) as context:
        context.write_sync(())

    assert context.get_buffer() == [
        {
            'a': 'a foo',
            'b': 'b foo',
            'c': 'c foo',
        }, {
            'a': 'a bar',
            'b': 'b bar',
            'c': 'c bar',
        }
    ]
