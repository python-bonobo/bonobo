import json
from collections import OrderedDict, namedtuple
from unittest import TestCase

import pytest

from bonobo import JsonReader, JsonWriter, LdjsonReader, LdjsonWriter
from bonobo.constants import EMPTY
from bonobo.util.testing import ConfigurableNodeTest, ReaderTest, WriterTest

FOOBAR = {"foo": "bar"}
OD_ABC = OrderedDict((("a", "A"), ("b", "B"), ("c", "C")))
FOOBAZ = {"foo": "baz"}

incontext = ConfigurableNodeTest.incontext


###
# Standard JSON Readers / Writers
###


class Json:
    extension = "json"
    ReaderNodeType = JsonReader
    WriterNodeType = JsonWriter


class JsonReaderDictsTest(Json, ReaderTest, TestCase):
    input_data = '[{"foo": "bar"},\n{"baz": "boz"}]'

    @incontext()
    def test_nofields(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [({"foo": "bar"},), ({"baz": "boz"},)]


class JsonReaderListsTest(Json, ReaderTest, TestCase):
    input_data = "[[1,2,3],\n[4,5,6]]"

    @incontext()
    def test_nofields(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [([1, 2, 3],), ([4, 5, 6],)]

    @incontext(output_type=tuple)
    def test_output_type(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [([1, 2, 3],), ([4, 5, 6],)]


class JsonReaderStringsTest(Json, ReaderTest, TestCase):
    input_data = "[" + ",\n".join(map(json.dumps, ("foo", "bar", "baz"))) + "]"

    @incontext()
    def test_nofields(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [("foo",), ("bar",), ("baz",)]

    @incontext(output_type=tuple)
    def test_output_type(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [("foo",), ("bar",), ("baz",)]


class JsonWriterTest(Json, WriterTest, TestCase):
    @incontext()
    def test_fields(self, context):
        context.set_input_fields(["foo", "bar"])
        context.write_sync(("a", "b"), ("c", "d"))
        context.stop()

        assert self.readlines() == ('[{"foo": "a", "bar": "b"},', '{"foo": "c", "bar": "d"}]')

    @incontext()
    def test_fields_from_type(self, context):
        context.set_input_type(namedtuple("Point", "x y"))
        context.write_sync((1, 2), (3, 4))
        context.stop()

        assert self.readlines() == ('[{"x": 1, "y": 2},', '{"x": 3, "y": 4}]')

    @incontext()
    def test_nofields_multiple_args(self, context):
        # multiple args are iterated onto and flattened in output
        context.write_sync((FOOBAR, FOOBAR), (OD_ABC, FOOBAR), (FOOBAZ, FOOBAR))
        context.stop()

        assert self.readlines() == (
            '[{"foo": "bar"},',
            '{"foo": "bar"},',
            '{"a": "A", "b": "B", "c": "C"},',
            '{"foo": "bar"},',
            '{"foo": "baz"},',
            '{"foo": "bar"}]',
        )

    @incontext()
    def test_nofields_multiple_args_length_mismatch(self, context):
        # if length of input vary, then we get a TypeError (unrecoverable)
        with pytest.raises(TypeError):
            context.write_sync((FOOBAR, FOOBAR), (OD_ABC))

    @incontext()
    def test_nofields_single_arg(self, context):
        # single args are just dumped, shapes can vary.
        context.write_sync(FOOBAR, OD_ABC, FOOBAZ)
        context.stop()

        assert self.readlines() == ('[{"foo": "bar"},', '{"a": "A", "b": "B", "c": "C"},', '{"foo": "baz"}]')

    @incontext()
    def test_nofields_empty_args(self, context):
        # empty calls are ignored
        context.write_sync(EMPTY, EMPTY, EMPTY)
        context.stop()

        assert self.readlines() == ("[]",)


###
# Line Delimiter JSON Readers / Writers
###


class Ldjson:
    extension = "ldjson"
    ReaderNodeType = LdjsonReader
    WriterNodeType = LdjsonWriter


class LdjsonReaderDictsTest(Ldjson, ReaderTest, TestCase):
    input_data = '{"foo": "bar"}\n{"baz": "boz"}'

    @incontext()
    def test_nofields(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [({"foo": "bar"},), ({"baz": "boz"},)]


class LdjsonReaderListsTest(Ldjson, ReaderTest, TestCase):
    input_data = "[1,2,3]\n[4,5,6]"

    @incontext()
    def test_nofields(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [([1, 2, 3],), ([4, 5, 6],)]

    @incontext(output_type=tuple)
    def test_output_type(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [([1, 2, 3],), ([4, 5, 6],)]


class LdjsonReaderStringsTest(Ldjson, ReaderTest, TestCase):
    input_data = "\n".join(map(json.dumps, ("foo", "bar", "baz")))

    @incontext()
    def test_nofields(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [("foo",), ("bar",), ("baz",)]

    @incontext(output_type=tuple)
    def test_output_type(self, context):
        context.write_sync(EMPTY)
        context.stop()

        assert context.get_buffer() == [("foo",), ("bar",), ("baz",)]


class LdjsonWriterTest(Ldjson, WriterTest, TestCase):
    @incontext()
    def test_fields(self, context):
        context.set_input_fields(["foo", "bar"])
        context.write_sync(("a", "b"), ("c", "d"))
        context.stop()

        assert self.readlines() == ('{"foo": "a", "bar": "b"}', '{"foo": "c", "bar": "d"}')

    @incontext()
    def test_fields_from_type(self, context):
        context.set_input_type(namedtuple("Point", "x y"))
        context.write_sync((1, 2), (3, 4))
        context.stop()

        assert self.readlines() == ('{"x": 1, "y": 2}', '{"x": 3, "y": 4}')

    @incontext()
    def test_nofields_multiple_args(self, context):
        # multiple args are iterated onto and flattened in output
        context.write_sync((FOOBAR, FOOBAR), (OD_ABC, FOOBAR), (FOOBAZ, FOOBAR))
        context.stop()

        assert self.readlines() == (
            '{"foo": "bar"}',
            '{"foo": "bar"}',
            '{"a": "A", "b": "B", "c": "C"}',
            '{"foo": "bar"}',
            '{"foo": "baz"}',
            '{"foo": "bar"}',
        )

    @incontext()
    def test_nofields_multiple_args_length_mismatch(self, context):
        # if length of input vary, then we get a TypeError (unrecoverable)
        with pytest.raises(TypeError):
            context.write_sync((FOOBAR, FOOBAR), (OD_ABC))

    @incontext()
    def test_nofields_single_arg(self, context):
        # single args are just dumped, shapes can vary.
        context.write_sync(FOOBAR, OD_ABC, FOOBAZ)
        context.stop()

        assert self.readlines() == ('{"foo": "bar"}', '{"a": "A", "b": "B", "c": "C"}', '{"foo": "baz"}')

    @incontext()
    def test_nofields_empty_args(self, context):
        # empty calls are ignored
        context.write_sync(EMPTY, EMPTY, EMPTY)
        context.stop()

        assert self.readlines() == ()
