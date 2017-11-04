from fs.errors import ResourceNotFound

from bonobo.config import Configurable, ContextProcessor, Option, Service
from bonobo.errors import UnrecoverableError


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
