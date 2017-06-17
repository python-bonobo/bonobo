import pickle

from bonobo.config import Option
from bonobo.config.processors import ContextProcessor
from bonobo.constants import NOT_MODIFIED
from bonobo.nodes.io.base import FileHandler, IOFormatEnabled
from bonobo.nodes.io.file import FileReader, FileWriter
from bonobo.util.objects import ValueHolder


class PickleHandler(FileHandler):
    """

    .. attribute:: item_names

        The names of the items in the pickle, if it is not defined in the first item of the pickle.

    """

    item_names = Option(tuple)


class PickleReader(IOFormatEnabled, FileReader, PickleHandler):
    """
    Reads a Python pickle object and yields the items in dicts.
    """

    mode = Option(str, default='rb')

    @ContextProcessor
    def pickle_headers(self, context, fs, file):
        yield ValueHolder(self.item_names)

    def read(self, fs, file, pickle_headers):
        data = pickle.load(file)

        # if the data is not iterable, then wrap the object in a list so it may be iterated
        if isinstance(data, dict):
            is_dict = True
            iterator = iter(data.items())
        else:
            is_dict = False
            try:
                iterator = iter(data)
            except TypeError:
                iterator = iter([data])

        if not pickle_headers.get():
            pickle_headers.set(next(iterator))

        item_count = len(pickle_headers.value)

        for i in iterator:
            if len(i) != item_count:
                raise ValueError('Received an object with %d items, expecting %d.' % (len(i), item_count, ))

            yield self.get_output(dict(zip(i)) if is_dict else dict(zip(pickle_headers.value, i)))


class PickleWriter(IOFormatEnabled, FileWriter, PickleHandler):
    mode = Option(str, default='wb')

    def write(self, fs, file, lineno, item):
        """
        Write a pickled item to the opened file.
        """
        file.write(pickle.dumps(item))
        lineno += 1
        return NOT_MODIFIED
