from bonobo import FileWriter, JsonFileWriter

to_file = FileWriter
to_json = JsonFileWriter

__all__ = [
    'to_json',
    'to_file',
]
