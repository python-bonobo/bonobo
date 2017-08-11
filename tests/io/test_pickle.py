import pickle

import pytest

from bonobo import Bag, PickleReader, PickleWriter, settings
from bonobo.constants import BEGIN, END
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import CapturingNodeExecutionContext, FilesystemTester

pickle_tester = FilesystemTester('pkl', mode='wb')
pickle_tester.input_data = pickle.dumps([['a', 'b', 'c'], ['a foo', 'b foo', 'c foo'], ['a bar', 'b bar', 'c bar']])


def test_write_pickled_dict_to_file(tmpdir):
    fs, filename, services = pickle_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(PickleWriter(filename, ioformat=settings.IOFORMAT_ARG0), services=services) as context:
        context.write(BEGIN, Bag({'foo': 'bar'}), Bag({'foo': 'baz', 'ignore': 'this'}), END)
        context.step()
        context.step()

    with fs.open(filename, 'rb') as fp:
        assert pickle.loads(fp.read()) == {'foo': 'bar'}

    with pytest.raises(AttributeError):
        getattr(context, 'file')


def test_read_pickled_list_from_file(tmpdir):
    fs, filename, services = pickle_tester.get_services_for_reader(tmpdir)

    with CapturingNodeExecutionContext(
        PickleReader(filename, ioformat=settings.IOFORMAT_ARG0), services=services
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
