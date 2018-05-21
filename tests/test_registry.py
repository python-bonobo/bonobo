from bonobo.nodes import CsvReader, JsonReader, CsvWriter, JsonWriter
from bonobo import create_reader, create_writer


def test_create_reader():
    t = create_reader('foo.csv')
    assert isinstance(t, CsvReader)

    t = create_reader('foo.txt', format='json')
    assert isinstance(t, JsonReader)


def test_create_writer():
    t = create_writer('foo.csv')
    assert isinstance(t, CsvWriter)

    t = create_writer('foo.txt', format='json')
    assert isinstance(t, JsonWriter)
