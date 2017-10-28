import pytest

from bonobo import JsonReader, JsonWriter, settings
from bonobo import LdjsonReader, LdjsonWriter
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import FilesystemTester, BufferingNodeExecutionContext

json_tester = FilesystemTester('json')
json_tester.input_data = '''[{"x": "foo"},{"x": "bar"}]'''


def test_write_json_ioformat_arg0(tmpdir):
    fs, filename, services = json_tester.get_services_for_writer(tmpdir)

    with pytest.raises(ValueError):
        JsonWriter(filename, ioformat=settings.IOFORMAT_ARG0)

    with pytest.raises(ValueError):
        JsonReader(filename, ioformat=settings.IOFORMAT_ARG0),


@pytest.mark.parametrize('add_kwargs', (
    {},
    {
        'ioformat': settings.IOFORMAT_KWARGS,
    },
))
def test_write_json_kwargs(tmpdir, add_kwargs):
    fs, filename, services = json_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(JsonWriter(filename, **add_kwargs), services=services) as context:
        context.write_sync({'foo': 'bar'})

    with fs.open(filename) as fp:
        assert fp.read() == '[{"foo": "bar"}]'


stream_json_tester = FilesystemTester('json')
stream_json_tester.input_data = '''{"foo": "bar"}\n{"baz": "boz"}'''


def test_read_stream_json(tmpdir):
    fs, filename, services = stream_json_tester.get_services_for_reader(tmpdir)
    with BufferingNodeExecutionContext(LdjsonReader(filename),
                                       services=services) as context:
        context.write_sync(tuple())
        actual = context.get_buffer()

    expected = [{"foo": "bar"}, {"baz": "boz"}]
    assert expected == actual


def test_write_stream_json(tmpdir):
    fs, filename, services = stream_json_tester.get_services_for_reader(tmpdir)

    with BufferingNodeExecutionContext(LdjsonWriter(filename),
                                       services=services) as context:
        context.write_sync({'foo': 'bar'})
        context.write_sync({'baz': 'boz'})

    expected = '''{"foo": "bar"}\n{"baz": "boz"}\n'''
    with fs.open(filename) as fin:
        actual = fin.read()
    assert expected == actual
