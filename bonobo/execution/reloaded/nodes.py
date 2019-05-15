import logging
import asyncio
import functools

from bonobo.execution.reloaded.executors import AsyncExecutor
from bonobo.execution.reloaded.tokens import begin, end, token
from bonobo.execution.reloaded.meta import get_all_meta

logger = logging.getLogger(__name__)

"""
TODO:

parallelism works, but :

- we dont send the end token anymore, so probably jobs never end
- if more than one slot is available, we still wait on FIRST_COMPLETED, which effectively lowers the parallelism level.

"""


class Node:
    def __init__(self, handler):
        self.handler = handler
        self.meta = get_all_meta(handler)

    def create_consume_and_send_coroutine(self, *, executor, consumer, outputs):
        """
        Create a coroutine that wraps a consumer coroutine but ties it to an executor and a set of outputs.
        When the consumer return (or yield) values, they are passed to the output queues.

        TODO XXX Should this be here ? Or maybe in executor ??? XXX

        """

        @functools.wraps(consumer)
        async def consume_and_send(input_value):
            nonlocal consumer, outputs
            try:
                async for output_value in consumer(input_value):
                    await executor.send(outputs, output_value)
            except Exception:
                logger.exception("Error during node async generator iteration.")

        return consume_and_send

    def log(self, func, *args):
        print("{}::{}".format(self.handler.__name__, func), *args)

    async def run(self, executor: AsyncExecutor, input, outputs):
        consumer = executor.create_async_generator_for(self.handler)
        consume_and_send = self.create_consume_and_send_coroutine(executor=executor, consumer=consumer, outputs=outputs)
        self.log("begin", self, consume_and_send)

        started = False
        runlevel = 0

        # Currently running coroutines and "parallel" meta, aka the maximum amount of coroutines currently running.
        # XXX this should be validated somehow, only positive integers are fine.
        pending = set()
        parallel = self.meta.get("parallel", 1)

        while not started or runlevel:
            # Retrieve the next input value in line. If more than one source node produce values piped into this, it's
            # still the input queue who is in charge to agregate. XXX this is probably not implemented yet in reloaded
            # executors. TODO
            input_value = await input.get()

            # First, if we got a "token" (data streaming control message), we pass it through, and handle it afterward.
            # The "runlevel" counts the amount of "begin" token received without a matching "end" token, to handle
            # non-linear graph smoothly.
            if isinstance(input_value, token):
                if input_value is begin:
                    await executor.send(outputs, input_value)
                    started = True
                    runlevel += 1
                elif input_value is end:
                    # await executor.send(outputs, input_value)
                    runlevel -= 1
                continue

            # While we're at our maximum parallelism level, try to finish some work first.
            while len(pending) >= parallel:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for finished in done:
                    self.log("done", finished)

            # We have at least one slot available to run more work.
            next = asyncio.ensure_future(consume_and_send(input_value))
            pending.add(next)
            self.log("next", next)

        if len(pending):
            self.log("pending after end", pending)
            done, pending = await asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)
            print("xxxxx", done, pending)
            for finished in done:
                print("done:", finished)

        print("<END>", self)

    def __repr__(self):
        return "<Node for " + repr(self.handler)[1:]
