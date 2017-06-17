from bonobo import settings
from bonobo.config import Configurable, ContextProcessor, Option, Service
from bonobo.structs.bags import Bag


class IOFormatEnabled(Configurable):
    ioformat = Option(default=settings.IOFORMAT.get)

    def get_input(self, *args, **kwargs):
        if self.ioformat == settings.IOFORMAT_ARG0:
            if len(args) != 1 or len(kwargs):
                raise ValueError(
                    'Wrong input formating: IOFORMAT=ARG0 implies one arg and no kwargs, got args={!r} and kwargs={!r}.'.
                    format(args, kwargs)
                )
            return args[0]

        if self.ioformat == settings.IOFORMAT_KWARGS:
            if len(args) or not len(kwargs):
                raise ValueError(
                    'Wrong input formating: IOFORMAT=KWARGS ioformat implies no arg, got args={!r} and kwargs={!r}.'.
                    format(args, kwargs)
                )
            return kwargs

        raise NotImplementedError('Unsupported format.')

    def get_output(self, row):
        if self.ioformat == settings.IOFORMAT_ARG0:
            return row

        if self.ioformat == settings.IOFORMAT_KWARGS:
            return Bag(**row)

        raise NotImplementedError('Unsupported format.')


class FileHandler(Configurable):
    """Abstract component factory for file-related components.

    Args:
        path (str): which path to use within the provided filesystem.
        eol (str): which character to use to separate lines.
        mode (str): which mode to use when opening the file.
        fs (str): service name to use for filesystem.
    """

    path = Option(str, required=True, positional=True)  # type: str
    eol = Option(str, default='\n')  # type: str
    mode = Option(str)  # type: str
    encoding = Option(str, default='utf-8')  # type: str
    fs = Service('fs')  # type: str

    @ContextProcessor
    def file(self, context, fs):
        with self.open(fs) as file:
            yield file

    def open(self, fs):
        return fs.open(self.path, self.mode, encoding=self.encoding)


class Reader:
    """Abstract component factory for readers.
    """

    def __call__(self, *args, **kwargs):
        yield from self.read(*args, **kwargs)

    def read(self, *args, **kwargs):
        raise NotImplementedError('Abstract.')


class Writer:
    """Abstract component factory for writers.
    """

    def __call__(self, *args, **kwargs):
        return self.write(*args, **kwargs)

    def write(self, *args, **kwargs):
        raise NotImplementedError('Abstract.')
