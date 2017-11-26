from bonobo.config import Configurable, ContextProcessor, Option, Service


class FileHandler(Configurable):
    """Abstract component factory for file-related components.

    Args:
        fs (str): service name to use for filesystem.
        path (str): which path to use within the provided filesystem.
        eol (str): which character to use to separate lines.
        mode (str): which mode to use when opening the file.
        encoding (str): which encoding to use when opening the file.
    """

    path = Option(str, required=True, positional=True)  # type: str
    eol = Option(str, default='\n')  # type: str
    mode = Option(str)  # type: str
    encoding = Option(str, default='utf-8')  # type: str

    fs = Service('fs')  # type: str

    @ContextProcessor
    def file(self, context, *, fs):
        with self.open(fs) as file:
            yield file

    def open(self, fs):
        return fs.open(self.path, self.mode, encoding=self.encoding)


class Reader:
    pass


class Writer:
    pass
