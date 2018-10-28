import argparse

import bonobo
from bonobo.execution.reloaded.executors import AsyncIOExecutor, TrioExecutor
from bonobo.execution.reloaded.jobs import Job

if __name__ == '__main__':
    import math

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.required = True
    group.add_argument('--asyncio', action='store_const', const=AsyncIOExecutor, dest='executor')
    group.add_argument('--trio', action='store_const', const=TrioExecutor, dest='executor')
    options = parser.parse_args()

    def produce_something(*args, **kwargs):
        for x in range(ord('a'), ord('z') + 1):
            for y in range(ord('a'), ord('z') + 1):
                yield chr(x), chr(y)

    async def make_it_awesome(v):
        yield v[0].upper(), v[1].upper(), math.sin(ord(v[0])), math.cos(ord(v[1]))

    async def reverse(x):
        yield x[::-1]

    graph = bonobo.Graph()
    graph.get_cursor() >> produce_something >> make_it_awesome >> reverse >> print
    job = Job(graph)
    options.executor().execute(job)