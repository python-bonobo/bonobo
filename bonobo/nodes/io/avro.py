from datetime import datetime, date, timedelta, time
from decimal import Decimal

from bonobo.config import Option, use_context
from bonobo.nodes.io.base import FileHandler
from bonobo.nodes.io.file import FileReader, FileWriter

# import fastavro
try:
    import fastavro
except ImportError:
    pass


class AvroHandler(FileHandler):
    schema = Option(tuple, required=False, 
        __doc__="A dict specifying the schema fields acording avro spec.\
        ```\
        schema = {\
            'doc': 'A weather reading.',\
            'name': 'Weather',\
            'namespace': 'test',\
            'type': 'record',\
            'fields': [\
                {'name': 'station', 'type': 'string'},\
                {'name': 'date', 'type': 'int', 'logicalType': 'date'},\
                {'name': 'time', 'type': 'long', 'logicalType': 'time-micros'},\
                {'name': 'temp', 'type': 'int'},\
            ],\
        }\
        ```\
        See: https://avro.apache.org/docs/current/spec.html#schema_primitive\
             https://avro.apache.org/docs/current/spec.html#Logical+Types")

    codec = Option(str, required=False, default="null", 
        __doc__="The name of the compression codec used to compress blocks.\
                Compression codec can be ‘null’, ‘deflate’ or ‘snappy’ (if installed)")


@use_context
class AvroReader(FileReader, AvroHandler):
    """
    Reads the records from a avro file and yields the values in dicts.
    """
    mode = Option(str, default="rb")

    def load_schema(self, context, avro_reader):
        file_schema = avro_reader.writer_schema
        self.schema = file_schema
        self.codec = avro_reader.codec
        schema_fields = file_schema['fields']
        field_names = [col['name'] for col in schema_fields]
        col_names = tuple(field_names)
        context.set_output_fields(col_names)

    def read(self, file, context, *, fs):
        avro_reader = fastavro.reader(file)
        if not context.output_type:
            self.load_schema(context, avro_reader)
        for record in avro_reader:
            row = tuple(record.values())
            yield row

    __call__ = read


@use_context
class AvroWriter(FileWriter, AvroHandler):
    """
    Writes the values as records into a avro file according to the fields defined in schema

    When the schema is not specified, it tries to guess types from the values
    of the fields present in the first record. 
    The type of values written follow the ones of python type system. Take
    care when writing data extracted from sql databases as their types are
    usually affected by factors like driver issues, type mismatch, incorrect
    mapping, precision loss (specially float and decimals), SQLArchitect...
    """
    compression_level = Option(int, required=False, 
        __doc__="Compression level to use when the specified codec supports it")

    mode = Option(str, default="wb+")

    def assure_same_len(self, props, values):
        if len(props) != len(values):
            m = "Values length differs from input fields length. Expected: {}. Got: {}. Values: {!r}."
            f = m.format(len(props), len(values), values)
            raise ValueError(m)

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
                f = {'name': p, 'type': 'int', 'logicalType': 'date'}
            elif isinstance(v, timedelta) or isinstance(v, time):
                f = {'name': p, 'type': 'long', 'logicalType': 'time-micros'}
            elif isinstance(v, datetime):
                f = {'name': p, 'type': 'long', 'logicalType': 'timestamp-micros'}
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

    def build_schema_from(self, props, values):
        if self.schema is not None:
            return self.schema
        schema_fields = self.build_schema_from_values(props, values)
        schema = {
            'type': 'record',
            'name': 'output',
            'namespace': "avro",
            'doc': "generated by bonobo",
            'fields': schema_fields,
        }
        return schema

    def write(self, file, context, *values, fs):
        """
        Write a record to the opened file using the defined schema
        """
        context.setdefault("schema", None)
        context.setdefault("converters", None)

        props = context.get_input_fields()
        if not context.schema:
            detected = self.build_schema_from(props, values)
            parsed = fastavro.parse_schema(detected)
            context.schema = parsed
        if not context.converters:
            context.converters = self.build_converters_from_values(values)
        row = {k: conv(v) for k, v, conv in zip(props, values, context.converters)}
        one_record = [row]
        fastavro.writer(
            fo=file, 
            schema=context.schema, 
            records=one_record, 
            codec=self.codec,
            codec_compression_level=self.compression_level
            )

    __call__ = write
