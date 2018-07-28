from bonobo.config import Configurable, Method, Option, ContextProcessor, use_raw_input
from bonobo.util import ValueHolder


class Reduce(Configurable):
    function = Method()
    initializer = Option(required=False)

    @ContextProcessor
    def buffer(self, context):
        values = yield ValueHolder(self.initializer() if callable(self.initializer) else self.initializer)
        context.send(values.get())

    @use_raw_input
    def __call__(self, values, bag):
        values.set(self.function(values.get(), bag))
