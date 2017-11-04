from contextlib import contextmanager

from bonobo import open_fs, Token
from bonobo.execution.contexts.graph import GraphExecutionContext
from bonobo.execution.contexts.node import NodeExecutionContext


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


class QueueList(list):
    def append(self, item):
        if not isinstance(item, Token):
            super(QueueList, self).append(item)

    put = append


class BufferingContext:
    def __init__(self, buffer=None):
        if buffer is None:
            buffer = QueueList()
        self.buffer = buffer

    def get_buffer(self):
        return self.buffer


class BufferingNodeExecutionContext(BufferingContext, NodeExecutionContext):
    def __init__(self, *args, buffer=None, **kwargs):
        BufferingContext.__init__(self, buffer)
        NodeExecutionContext.__init__(self, *args, **kwargs, _outputs=[self.buffer])


class BufferingGraphExecutionContext(BufferingContext, GraphExecutionContext):
    NodeExecutionContextType = BufferingNodeExecutionContext

    def __init__(self, *args, buffer=None, **kwargs):
        BufferingContext.__init__(self, buffer)
        GraphExecutionContext.__init__(self, *args, **kwargs)

    def create_node_execution_context_for(self, node):
        return self.NodeExecutionContextType(node, parent=self, buffer=self.buffer)
