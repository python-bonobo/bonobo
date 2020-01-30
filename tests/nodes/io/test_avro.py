import pytest
from datetime import datetime, date, timedelta

from bonobo import AvroReader, AvroWriter
from bonobo.constants import EMPTY
from bonobo.execution.contexts.node import NodeExecutionContext
from bonobo.util.testing import BufferingNodeExecutionContext, FilesystemTester

avro_tester = FilesystemTester("avro", mode="wb")
# avro_tester.input_data = pickle.dumps([["a", "b", "c"], ["a foo", "b foo", "c foo"], ["a bar", "b bar", "c bar"]])


def test_write_records_to_avro_file(tmpdir):
    fs, filename, services = avro_tester.get_services_for_writer(tmpdir)

    john = ("john", 7, date(2012,10,11), datetime(2012,10,11,15,16,17))
    jane = ("jane", 17, date(2002,10,11), datetime(2002,10,13,15,16,17))

    writav = AvroWriter(filename)
    with NodeExecutionContext(writav, services=services) as context:
        context.set_input_fields(["name", "age", "birthday", "registered"])
        context.write_sync(john, jane)

    # with fs.open(filename, "rb") as fp:
        # assert pickle.loads(fp.read()) == {"foo": "bar"}


def create_avro_example(path):
    import fastavro

    schema = {
        'doc': 'A weather reading.',
        'name': 'Weather',
        'namespace': 'test',
        'type': 'record',
        'fields': [
            {'name': 'station', 'type': 'string'},
            {'name': 'time', 'type': 'long'},
            {'name': 'temp', 'type': 'int'},
        ],
    }
    parsed_schema = fastavro.parse_schema(schema)

    records = [
        {u'station': u'cold', u'temp': 0, u'time': 1433269388},
        {u'station': u'warm', u'temp': 22, u'time': 1433270389},
        {u'station': u'frozen', u'temp': -11, u'time': 1433273379},
        {u'station': u'hot', u'temp': 111, u'time': 1433275478},
    ]

    with open(path, 'wb') as out:
        fastavro.writer(out, parsed_schema, records)


def test_read_records_from_avro_file(tmpdir):
    dst = tmpdir.strpath + '/output.avro'
    create_avro_example(dst)

    fs, filename, services = avro_tester.get_services_for_writer(tmpdir)

    readav = AvroReader(filename)
    with BufferingNodeExecutionContext(readav, services=services) as context:
        context.write_sync(EMPTY)

    output = context.get_buffer()
    props = context.get_output_fields()
    assert props == ("station", "time", "temp")
    # assert output == [("a foo", "b foo", "c foo"), ("a bar", "b bar", "c bar")]
