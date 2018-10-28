import logging

from bonobo.execution.reloaded.executors import AsyncExecutor
from bonobo.execution.reloaded.tokens import begin, end, token

logger = logging.getLogger(__name__)


class Node:
    def __init__(self, handler):
        self.handler = handler

    async def run(self, executor: AsyncExecutor, input, outputs):
        consumer = executor.create_async_generator_for(self.handler)
        print('<BEGIN>', self, consumer)

        started = False
        runlevel = 0

        while not started or runlevel:
            value = await input.get()

            # tokens are passed unchanged
            if isinstance(value, token):
                await executor.send(outputs, value)
                if value is begin:
                    started = True
                    runlevel += 1
                elif value is end:
                    runlevel -= 1
                continue

            try:
                async for pending in consumer(value):
                    await executor.send(outputs, pending)
            except Exception:
                logger.exception('Wops')

        print('<END>', self)

    def __repr__(self):
        return "<Node for " + repr(self.handler)[1:]
