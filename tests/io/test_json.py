import pytest

from bonobo import Bag, JsonReader, JsonWriter, settings
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext, FilesystemTester

json_tester = FilesystemTester('json')
json_tester.input_data = '''[{"x": "foo"},{"x": "bar"}]'''


def test_write_json_arg0(tmpdir):
    fs, filename, services = json_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(JsonWriter(filename, ioformat=settings.IOFORMAT_ARG0), services=services) as context:
        context.write(BEGIN, Bag({'foo': 'bar'}), END)
        context.step()

    with fs.open(filename) as fp:
        assert fp.read() == '[{"foo": "bar"}]'


@pytest.mark.parametrize('add_kwargs', (
    {},
    {
        'ioformat': settings.IOFORMAT_KWARGS,
    },
))
def test_write_json_kwargs(tmpdir, add_kwargs):
    fs, filename, services = json_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(JsonWriter(filename, **add_kwargs), services=services) as context:
        context.write(BEGIN, Bag(**{'foo': 'bar'}), END)
        context.step()

    with fs.open(filename) as fp:
        assert fp.read() == '[{"foo": "bar"}]'


def test_read_json_arg0(tmpdir):
    fs, filename, services = json_tester.get_services_for_reader(tmpdir)

    with CapturingNodeExecutionContext(
        JsonReader(filename, ioformat=settings.IOFORMAT_ARG0),
        services=services,
    ) as context:
        context.write(BEGIN, Bag(), END)
        context.step()

    assert len(context.send.mock_calls) == 2

    args0, kwargs0 = context.send.call_args_list[0]
    assert len(args0) == 1 and not len(kwargs0)
    args1, kwargs1 = context.send.call_args_list[1]
    assert len(args1) == 1 and not len(kwargs1)

    assert args0[0].args[0] == {'x': 'foo'}
    assert args1[0].args[0] == {'x': 'bar'}
