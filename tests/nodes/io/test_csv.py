from collections import namedtuple
from csv import QUOTE_ALL
from unittest import TestCase

import pytest

from bonobo import CsvReader, CsvWriter
from bonobo.constants import EMPTY
from bonobo.util.testing import (
    BufferingNodeExecutionContext, ConfigurableNodeTest, FilesystemTester, ReaderTest, WriterTest
)

csv_tester = FilesystemTester("csv")
csv_tester.input_data = "a,b,c\na foo,b foo,c foo\na bar,b bar,c bar"

defaults = {"lineterminator": "\n"}

incontext = ConfigurableNodeTest.incontext


def test_read_csv_from_file_kwargs(tmpdir):
    fs, filename, services = csv_tester.get_services_for_reader(tmpdir)

    with BufferingNodeExecutionContext(CsvReader(filename, **defaults), services=services) as context:
        context.write_sync(EMPTY)

    assert context.get_buffer_args_as_dicts() == [
        {"a": "a foo", "b": "b foo", "c": "c foo"},
        {"a": "a bar", "b": "b bar", "c": "c bar"},
    ]


###
# CSV Readers / Writers
###


class Csv:
    extension = "csv"
    ReaderNodeType = CsvReader
    WriterNodeType = CsvWriter


L1, L2, L3, L4 = ("a", "hey"), ("b", "bee"), ("c", "see"), ("d", "dee")
LL = ("i", "have", "more", "values")


class CsvReaderTest(Csv, ReaderTest, TestCase):
    input_data = "\n".join(("id,name", "1,John Doe", "2,Jane Doe", ",DPR", "42,Elon Musk"))

    def check_output(self, context, *, prepend=None):
        out = context.get_buffer()
        assert out == (prepend or list()) + [("1", "John Doe"), ("2", "Jane Doe"), ("", "DPR"), ("42", "Elon Musk")]

    @incontext()
    def test_nofields(self, context):
        context.write_sync(EMPTY)
        context.stop()
        self.check_output(context)
        assert context.get_output_fields() == ("id", "name")

    @incontext(output_type=tuple)
    def test_output_type(self, context):
        context.write_sync(EMPTY)
        context.stop()
        self.check_output(context, prepend=[("id", "name")])

    @incontext(output_fields=("x", "y"), skip=1)
    def test_output_fields(self, context):
        context.write_sync(EMPTY)
        context.stop()
        self.check_output(context)
        assert context.get_output_fields() == ("x", "y")

    @incontext(quoting=QUOTE_ALL)
    def test_quoting(self, context):
        context.write_sync(EMPTY)
        context.stop()
        self.check_output(context)
        assert context.get_output_fields() == ("id", "name")


class CsvWriterTest(Csv, WriterTest, TestCase):
    @incontext()
    def test_fields(self, context):
        context.set_input_fields(["foo", "bar"])
        context.write_sync(("a", "b"), ("c", "d"))
        context.stop()

        assert self.readlines() == ("foo,bar", "a,b", "c,d")

    @incontext(skip_header=False)
    def test_fields_with_headers(self, context):
        context.set_input_fields(["foo", "bar"])
        context.write_sync(("a", "b"), ("c", "d"))
        context.stop()

        assert self.readlines() == ("foo,bar", "a,b", "c,d")

    @incontext(skip_header=True)
    def test_fields_without_headers(self, context):
        context.set_input_fields(["foo", "bar"])
        context.write_sync(("a", "b"), ("c", "d"))
        context.stop()

        assert self.readlines() == ("a,b", "c,d")

    @incontext()
    def test_fields_from_type(self, context):
        context.set_input_type(namedtuple("Point", "x y"))
        context.write_sync((1, 2), (3, 4))
        context.stop()

        assert self.readlines() == ("x,y", "1,2", "3,4")

    @incontext()
    def test_nofields_multiple_args(self, context):
        # multiple args are iterated onto and flattened in output
        context.write_sync(L1, L2, L3, L4)
        context.stop()

        assert self.readlines() == ("a,hey", "b,bee", "c,see", "d,dee")

    @incontext()
    def test_nofields_multiple_args_length_mismatch(self, context):
        # if length of input vary, then we get a TypeError (unrecoverable)
        with pytest.raises(TypeError):
            context.write_sync((L1, L2), (L3,))

    @incontext()
    def test_nofields_empty_args(self, context):
        # empty calls are ignored
        context.write_sync(EMPTY, EMPTY, EMPTY)
        context.stop()

        assert self.readlines() == ("", "", "")
