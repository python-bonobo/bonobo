import bonobo


def extract():
    yield 'foo'
    yield 'bar'
    yield 'baz'


def transform(x):
    return x.upper()


def load(x):
    print(x)


graph = bonobo.Graph(extract, transform, load)

graph.__doc__ = 'hello'

if __name__ == '__main__':
    bonobo.run(graph)
