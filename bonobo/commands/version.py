import bonobo


def execute():
    print('{} v.{}'.format(bonobo.__name__, bonobo.__version__))


def register(parser):
    return execute
