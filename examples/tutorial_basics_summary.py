from bonobo import Graph, ThreadPoolExecutorStrategy


def yield_from(*args):
    yield from args


# Represent our data processor as a simple directed graph of callables.
graph = Graph(
    lambda: (x for x in ('foo', 'bar', 'baz')),
    str.upper,
    print,
)

# Use a thread pool.
executor = ThreadPoolExecutorStrategy()

# Run the thing.
executor.execute(graph)
