import mimetypes
import os

from bonobo import CsvReader, CsvWriter, FileReader, FileWriter, JsonReader, JsonWriter, PickleReader, PickleWriter

FILETYPE_CSV = 'text/csv'
FILETYPE_JSON = 'application/json'
FILETYPE_PICKLE = 'pickle'
FILETYPE_PLAIN = 'text/plain'

READER = 'reader'
WRITER = 'writer'


class Registry:
    ALIASES = {
        'csv': FILETYPE_CSV,
        'json': FILETYPE_JSON,
        'pickle': FILETYPE_PICKLE,
        'plain': FILETYPE_PLAIN,
        'text': FILETYPE_PLAIN,
        'txt': FILETYPE_PLAIN,
    }

    FACTORIES = {
        READER: {
            FILETYPE_JSON: JsonReader,
            FILETYPE_CSV: CsvReader,
            FILETYPE_PICKLE: PickleReader,
            FILETYPE_PLAIN: FileReader,
        },
        WRITER: {
            FILETYPE_JSON: JsonWriter,
            FILETYPE_CSV: CsvWriter,
            FILETYPE_PICKLE: PickleWriter,
            FILETYPE_PLAIN: FileWriter,
        },
    }

    def get_factory_for(self, kind, name, *, format=None):
        if not kind in self.FACTORIES:
            raise KeyError('Unknown factory kind {!r}.'.format(kind))

        if format is None and name is None:
            raise RuntimeError('Cannot guess factory without at least a filename or a format.')

        # Guess mimetype if possible
        if format is None:
            format = mimetypes.guess_type(name)[0]

        # Guess from extension if possible
        if format is None:
            _, _ext = os.path.splitext(name)
            if _ext:
                format = _ext[1:]

        # Apply aliases
        if format in self.ALIASES:
            format = self.ALIASES[format]

        if format is None or not format in self.FACTORIES[kind]:
            raise RuntimeError(
                'Could not resolve {kind} factory for {name} ({format}).'.format(kind=kind, name=name, format=format)
            )

        return self.FACTORIES[kind][format]

    def get_reader_factory_for(self, name, *, format=None):
        """
        Returns a callable to build a reader for the provided filename, eventually forcing a format.

        :param name: filename
        :param format: format
        :return: type
        """
        return self.get_factory_for(READER, name, format=format)

    def get_writer_factory_for(self, name, *, format=None):
        """
        Returns a callable to build a writer for the provided filename, eventually forcing a format.

        :param name: filename
        :param format: format
        :return: type
        """
        return self.get_factory_for(WRITER, name, format=format)


default_registry = Registry()
