import pickle

import pytest

from bonobo import Bag, PickleReader, PickleWriter
from bonobo.execution.node import NodeExecutionContext
from bonobo.util.testing import BufferingNodeExecutionContext, FilesystemTester

pickle_tester = FilesystemTester('pkl', mode='wb')
pickle_tester.input_data = pickle.dumps([['a', 'b', 'c'], ['a foo', 'b foo', 'c foo'], ['a bar', 'b bar', 'c bar']])


def test_write_pickled_dict_to_file(tmpdir):
    fs, filename, services = pickle_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(PickleWriter(filename), services=services) as context:
        context.write_sync(Bag({'foo': 'bar'}), Bag({'foo': 'baz', 'ignore': 'this'}))

    with fs.open(filename, 'rb') as fp:
        assert pickle.loads(fp.read()) == {'foo': 'bar'}

    with pytest.raises(AttributeError):
        getattr(context, 'file')


def test_read_pickled_list_from_file(tmpdir):
    fs, filename, services = pickle_tester.get_services_for_reader(tmpdir)

    with BufferingNodeExecutionContext(PickleReader(filename), services=services) as context:
        context.write_sync(Bag())
        output = context.get_buffer()

    assert len(output) == 2
    assert output[0] == {
        'a': 'a foo',
        'b': 'b foo',
        'c': 'c foo',
    }
    assert output[1] == {
        'a': 'a bar',
        'b': 'b bar',
        'c': 'c bar',
    }
