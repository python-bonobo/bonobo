import pickle

from bonobo.config import Option, use_context
from bonobo.constants import NOT_MODIFIED
from bonobo.nodes.io.base import FileHandler
from bonobo.nodes.io.file import FileReader, FileWriter


class PickleHandler(FileHandler):
    """

    .. attribute:: item_names

        The names of the items in the pickle, if it is not defined in the first item of the pickle.

    """

    fields = Option(tuple, required=False)


@use_context
class PickleReader(FileReader, PickleHandler):
    """
    Reads a Python pickle object and yields the items in dicts.
    """

    mode = Option(str, default='rb')

    def read(self, file, context, *, fs):
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

        if not context.output_type:
            context.set_output_fields(self.fields or next(iterator))
        fields = context.get_output_fields()
        fields_length = len(fields)

        for row in iterator:
            if len(row) != fields_length:
                raise ValueError('Received an object with {} items, expected {}.'.format(len(row), fields_length))

            yield tuple(row.values() if is_dict else row)

    __call__ = read


@use_context
class PickleWriter(FileWriter, PickleHandler):
    mode = Option(str, default='wb')

    def write(self, file, context, item, *, fs):
        """
        Write a pickled item to the opened file.
        """
        context.setdefault('lineno', 0)
        file.write(pickle.dumps(item))
        context.lineno += 1
        return NOT_MODIFIED

    __call__ = write
