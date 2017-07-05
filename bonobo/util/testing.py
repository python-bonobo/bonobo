from contextlib import contextmanager
from unittest.mock import MagicMock

from bonobo import open_fs
from bonobo.execution.node import NodeExecutionContext


class CapturingNodeExecutionContext(NodeExecutionContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.send = MagicMock()


@contextmanager
def optional_contextmanager(cm, *, ignore=False):
    if cm is None or ignore:
        yield
    else:
        with cm:
            yield


class FilesystemTester:
    def __init__(self, extension='txt', mode='w'):
        self.extension = extension
        self.input_data = ''
        self.mode = mode

    def get_services_for_reader(self, tmpdir):
        fs, filename = open_fs(tmpdir), 'input.' + self.extension
        with fs.open(filename, self.mode) as fp:
            fp.write(self.input_data)
        return fs, filename, {'fs': fs}

    def get_services_for_writer(self, tmpdir):
        fs, filename = open_fs(tmpdir), 'output.' + self.extension
        return fs, filename, {'fs': fs}
