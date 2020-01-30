from datetime import datetime, date, timedelta, time
from decimal import Decimal

from bonobo.config import Option, use_context
from bonobo.nodes.io.base import FileHandler
from bonobo.nodes.io.file import FileReader, FileWriter
from bonobo.util.collections import coalesce

import fastavro


class AvroHandler(FileHandler):
    """

    .. attribute:: item_names

        The names of the items in the Avro, if it is not defined in the first item of the Avro.

    """

    fields = Option(tuple, required=False)
    types = Option(tuple, required=False)
    name = Option(str, required=False)
    namespace = Option(str, required=False)
    doc = Option(str, required=False)
    codec = Option(str, required=False, default="null")


@use_context
class AvroReader(FileReader, AvroHandler):
    """
    Reads a record from avro file and yields the rows in dicts.
    """

    mode = Option(str, default="rb")

    def load_schema(self, context, avro_reader):
        aschema = avro_reader.schema
        if 'doc' in aschema:
            self.doc = aschema['doc']
        if 'name' in aschema:
            self.name = aschema['name']
        if 'namespace' in aschema:
            self.namespace = aschema['namespace']
        src = aschema['fields']
        dst = [f['name'] for f in src]
        tfields = tuple(dst)
        context.set_output_fields(tfields)

    def read(self, file, context, *, fs):
        avro_reader = fastavro.reader(file)
        if not context.output_type:
            self.load_schema(context, avro_reader)

        for row in avro_reader:
            yield tuple(row)

    __call__ = read


@use_context
class AvroWriter(FileWriter, AvroHandler):

    mode = Option(str, default="wb+")

    def assure_same_len(self, props, values):
        if len(props) != len(values):
            raise ValueError(
                "Values length differs from input fields length. Expected: {}. Got: {}. Values: {!r}.".format(
                    len(props), len(values), values
                )
            )

    def build_schema_from_types(self, props):
        schema_fields = []
        for p, t in zip(props, self.types):
            if  isinstance(t, dict):
                f = t
                f['name'] = p
            elif t == "date":
                f = {'name': p, 'type': 'int', "logicalType": "date"}
            elif t == "time-micros":
                f = {'name': p, 'type': 'long', "logicalType": "time-micros"}
            elif t == "timestamp-micros":
                f = {'name': p, 'type': 'long', "logicalType": "timestamp-micros"}
            else:
                f = {'name': p, 'type': t}
            schema_fields.append(f)
        return schema_fields

    def build_schema_from_values(self, props, values):
        # https://avro.apache.org/docs/current/spec.html#schema_primitive
        self.assure_same_len(props, values)
        schema_fields = []
        for p, v in zip(props, values):
            if isinstance(v, int):
                f = {'name': p, 'type': 'long'}
            elif isinstance(v, bool):
                f = {'name': p, 'type': 'boolean'}
            elif isinstance(v, float):
                f = {'name': p, 'type': 'double'}
            elif isinstance(v, date):
                f = {'name': p, 'type': 'int', "logicalType": "date"}
            elif isinstance(v, timedelta) or isinstance(v, time):
                f = {'name': p, 'type': 'long', "logicalType": "time-micros"}
            elif isinstance(v, datetime):
                f = {'name': p, 'type': 'long', "logicalType": "timestamp-micros"}
            elif isinstance(v, Decimal):
                f = {'name': p, 'type': 'double'}
            elif isinstance(v, bytes):
                f = {'name': p, 'type': 'bytes'}
            else:
                f = {'name': p, 'type': 'string'}
            schema_fields.append(f)
        return schema_fields

    def build_converters_from_values(self, values):
        converters = []
        for v in values:
            if isinstance(v, datetime):
                f = AvroWriter.get_value_as_datetime
            elif isinstance(v, time):
                f = AvroWriter.get_value_as_time
            elif isinstance(v, timedelta):
                f = AvroWriter.get_value_as_timedelta
            elif isinstance(v, date):
                f = AvroWriter.get_value_as_date
            elif isinstance(v, Decimal):
                f = AvroWriter.get_value_as_float
            else:
                f = AvroWriter.get_same_value
            converters.append(f)
        return converters

    @staticmethod
    def get_same_value(value):
        return value

    @staticmethod
    def get_value_as_date(value):
        diff = value - date(1970,1,1)
        return diff.days

    @staticmethod
    def get_value_as_datetime(value):
        elapsed = value.timestamp()
        return int(elapsed)

    @staticmethod
    def get_value_as_timedelta(value):
        elapsed = (value.days * 86400000) + (value.seconds * 1000) + value.microseconds
        return elapsed

    @staticmethod
    def get_value_as_time(value):
        elapsed = (value.hour * 3600000) + (value.minute * 60000) + (value.second * 1000) + value.microsecond
        return elapsed

    @staticmethod
    def get_value_as_float(value):
        return float(value)

    def build_schema(self, props, values):

        if self.types is not None:
            schema_fields = self.build_schema_from_types(props)
        else:
            schema_fields = self.build_schema_from_values(props, values)

        schema = {
            'type': 'record',
            'name': coalesce(self.name, "output"),
            'namespace':  coalesce(self.namespace, "avro"),
            'doc': coalesce(self.doc, "generated by bonobo"),
            'fields': schema_fields,
        }
        return schema

    def get_write_fields(self, context):
        props = coalesce(self.fields, context.get_input_fields())
        return props

    def write(self, file, context, *values, fs):
        """
        Write a record to the opened file.
        """
        props = self.get_write_fields(context)

        context.setdefault("schema", None)
        if not context.schema:
            aschema = self.build_schema(props, values)
            parsed_schema = fastavro.parse_schema(aschema)
            context.schema = parsed_schema

        context.setdefault("converters", None)
        if not context.converters:
            context.converters = self.build_converters_from_values(values)

        kv = {k: conv(v) for k, v, conv in zip(props, values, context.converters)}

        row = [kv]
        fastavro.writer(fo=file, schema=context.schema, records=row, codec=self.codec)

    __call__ = write
