import pickle

from bonobo.config.processors import ContextProcessor
from bonobo.config import Option
from bonobo.constants import NOT_MODIFIED
from bonobo.util.objects import ValueHolder
from .file import FileReader, FileWriter, FileHandler


class PickleHandler(FileHandler):
    """

    .. attribute:: item_names

        The names of the items in the pickle, if it is not defined in the first item of the pickle.

    """

    item_names = Option(tuple)


class PickleReader(PickleHandler, FileReader):
    """
    Reads a Python pickle object and yields the items in dicts.
    """

    mode = Option(str, default='rb')

    @ContextProcessor
    def pickle_items(self, context, fs, file):
        yield ValueHolder(self.item_names)

    def read(self, fs, file, item_names):
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

        if not item_names.get():
            item_names.set(next(iterator))

        item_count = len(item_names.value)

        for i in iterator:
            if len(i) != item_count:
                raise ValueError('Received an object with %d items, expecting %d.' % (len(i), item_count, ))

            yield dict(zip(i)) if is_dict else dict(zip(item_names.value, i))


class PickleWriter(PickleHandler, FileWriter):

    mode = Option(str, default='wb')

    def write(self, fs, file, itemno, item):
        """
        Write a pickled item to the opened file.
        """
        file.write(pickle.dumps(item))
        itemno += 1
        return NOT_MODIFIED
