import pytest

from bonobo import JsonReader, JsonWriter, settings
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import FilesystemTester

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
