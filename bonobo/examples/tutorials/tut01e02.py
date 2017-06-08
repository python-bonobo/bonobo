import bonobo

graph = bonobo.Graph(
    [
        'foo',
        'bar',
        'baz',
    ],
    str.upper,
    print,
)

if __name__ == '__main__':
    bonobo.run(graph)
