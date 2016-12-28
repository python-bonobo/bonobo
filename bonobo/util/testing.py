from unittest.mock import MagicMock

from bonobo.core.contexts import ComponentExecutionContext


class CapturingComponentExecutionContext(ComponentExecutionContext):
    def __init__(self, component, parent):
        super().__init__(component, parent)
        self.send = MagicMock()
