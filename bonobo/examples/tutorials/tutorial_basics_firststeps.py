from bonobo import run


def generate_data():
    yield 'foo'
    yield 'bar'
    yield 'baz'


def uppercase(x: str):
    return x.upper()


def output(x: str):
    print(x)


run(generate_data, uppercase, output)
