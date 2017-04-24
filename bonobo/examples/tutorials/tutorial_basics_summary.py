import bonobo

# Represent our data processor as a simple directed graph of callables.
graph = bonobo.Graph(
    ['foo', 'bar', 'baz'],
    str.upper,
    print,
)

if __name__ == '__main__':
    bonobo.run(graph)
