import pickle

import pytest

from bonobo import PickleReader, PickleWriter
from bonobo.constants import EMPTY
from bonobo.execution.contexts.node import NodeExecutionContext
from bonobo.util.testing import BufferingNodeExecutionContext, FilesystemTester

pickle_tester = FilesystemTester("pkl", mode="wb")
pickle_tester.input_data = pickle.dumps([["a", "b", "c"], ["a foo", "b foo", "c foo"], ["a bar", "b bar", "c bar"]])


def test_write_pickled_dict_to_file(tmpdir):
    fs, filename, services = pickle_tester.get_services_for_writer(tmpdir)

    with NodeExecutionContext(PickleWriter(filename), services=services) as context:
        context.write_sync({"foo": "bar"}, {"foo": "baz", "ignore": "this"})

    with fs.open(filename, "rb") as fp:
        assert pickle.loads(fp.read()) == {"foo": "bar"}

    with pytest.raises(AttributeError):
        getattr(context, "file")


def test_read_pickled_list_from_file(tmpdir):
    fs, filename, services = pickle_tester.get_services_for_reader(tmpdir)

    with BufferingNodeExecutionContext(PickleReader(filename), services=services) as context:
        context.write_sync(EMPTY)

    output = context.get_buffer()
    assert context.get_output_fields() == ("a", "b", "c")
    assert output == [("a foo", "b foo", "c foo"), ("a bar", "b bar", "c bar")]
