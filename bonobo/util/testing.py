from contextlib import contextmanager
from unittest.mock import MagicMock

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
