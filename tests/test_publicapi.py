import inspect


def test_wildcard_import():
    bonobo = __import__('bonobo')
    assert bonobo.__version__

    for name in dir(bonobo):
        # ignore attributes starting by underscores
        if name.startswith('_'):
            continue
        attr = getattr(bonobo, name)
        if inspect.ismodule(attr):
            continue

        assert name in bonobo.__all__
