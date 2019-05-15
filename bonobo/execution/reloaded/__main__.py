"""
Last benchmarks:

asyncio: 5514629 function calls in 7.624 seconds
uvloop:  3794316 function calls (3794281 primitive calls) in 5.951 seconds
trio:    8375741 function calls (8354390 primitive calls) in 12.370 seconds

"""

import argparse

import bonobo
from bonobo.execution.reloaded.executors import AsyncIOExecutor, TrioExecutor, UVLoopAsyncIOExecutor
from bonobo.execution.reloaded.jobs import Job

if __name__ == "__main__":
    import math

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.required = True
    group.add_argument("--asyncio", action="store_const", const=AsyncIOExecutor, dest="executor")
    group.add_argument("--asyncio-uvloop", action="store_const", const=UVLoopAsyncIOExecutor, dest="executor")
    group.add_argument("--trio", action="store_const", const=TrioExecutor, dest="executor")
    options = parser.parse_args()

    def produce_something(*args, **kwargs):
        for x in range(ord("a"), ord("z") + 1):
            for y in range(ord("a"), ord("z") + 1):
                for z in range(ord("a"), ord("z") + 1):
                    yield chr(x), chr(y), chr(z)

    async def make_it_awesome(v):
        yield v[0].upper(), v[1].upper(), v[2].upper(), math.sin(ord(v[0])), math.cos(ord(v[1])), math.tan(ord(v[2]))

    async def reverse(x):
        yield x[::-1]

    graph = bonobo.Graph()
    graph.get_cursor() >> produce_something >> make_it_awesome >> reverse >> print
    job = Job(graph)

    import cProfile

    cProfile.run("options.executor().execute(job)", sort="tottime")

