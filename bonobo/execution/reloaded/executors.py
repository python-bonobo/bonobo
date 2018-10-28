import functools
import inspect
from concurrent.futures import ThreadPoolExecutor

from bonobo.constants import BEGIN
from bonobo.execution.reloaded.tokens import begin, end


class AsyncExecutor:
    def run_in_thread(self, x, *args, **kwargs):
        raise NotImplementedError('Concrete implementations should define this.')

    def create_async_generator_for(self, handler):
        # async generator
        if inspect.isasyncgenfunction(handler):
            return handler

        # async function
        if inspect.iscoroutinefunction(handler):

            @functools.wraps(handler)
            async def _asyncgen_coroutine_consumer(*args, **kwargs):
                nonlocal handler
                yield (await handler(*args, **kwargs))

            return _asyncgen_coroutine_consumer

        # generator
        if inspect.isgeneratorfunction(handler):

            @functools.wraps(handler)
            async def _asyncgen_generator_consumer(*args, **kwargs):
                nonlocal handler
                for x in handler(*args, **kwargs):
                    yield x

            return _asyncgen_generator_consumer

        # function
        if callable(handler):

            @functools.wraps(handler)
            async def _asyncgen_consumer(*args, **kwargs):
                nonlocal handler
                yield await self.run_in_thread(handler, *args, **kwargs)

            return _asyncgen_consumer

        raise NotImplementedError(repr(handler))

    def create_channel(self):
        raise NotImplementedError('Concrete implementations should define this.')

    def create_channels(self, job):
        inputs = {i: self.create_channel() for i in range(len(job.nodes))}
        outputs = {i: [inputs[j] for j in job.graph.outputs_of(i)] for i in range(len(job.nodes))}
        return inputs, outputs

    async def send(self, queues, value):
        for queue in queues:
            await queue.put(value)


class AsyncIOExecutor(AsyncExecutor):
    def __init__(self, *, loop=None):
        import asyncio

        self.asyncio = asyncio
        self.loop = loop or asyncio.get_event_loop()
        self.thread_pool_executor = ThreadPoolExecutor()

    def run_in_thread(self, x, *args, **kwargs):
        return self.loop.run_in_executor(self.thread_pool_executor, functools.partial(x, *args, **kwargs))

    def create_channel(self):
        return self.asyncio.Queue(maxsize=128)

    def execute(self, job):
        asyncio = self.asyncio
        inputs, outputs = self.create_channels(job)

        async def start():
            for i in job.graph.outputs_of(BEGIN):
                await inputs[i].put(begin)
                await inputs[i].put(())
                await inputs[i].put(end)

        futures = [asyncio.ensure_future(start())]
        for i, node in enumerate(job.nodes):
            futures.append(asyncio.ensure_future(node.run(self, inputs[i], outputs[i])))

        self.loop.run_until_complete(asyncio.wait(futures))


class TrioExecutor(AsyncExecutor):
    def __init__(self):
        import trio

        self.trio = trio

    def run_in_thread(self, x, *args, **kwargs):
        return self.trio.run_sync_in_worker_thread(functools.partial(x, *args, **kwargs))

    def create_channel(self):
        return self.trio.Queue(capacity=128)

    def execute(self, job):
        trio = self.trio
        inputs, outputs = self.create_channels(job)

        async def start():
            for i in job.graph.outputs_of(BEGIN):
                await inputs[i].put(begin)
                await inputs[i].put(())
                await inputs[i].put(end)

        async def call_the_nurse():
            async with trio.open_nursery() as nursery:
                nursery.start_soon(start)
                for i, node in enumerate(job.nodes):
                    nursery.start_soon(node.run, self, inputs[i], outputs[i])

        trio.run(call_the_nurse)
