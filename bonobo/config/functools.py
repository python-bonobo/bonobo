import functools
import itertools


def transformation_factory(f):
    @functools.wraps(f)
    def _transformation_factory(*args, **kwargs):
        retval = f(*args, **kwargs)
        retval.__name__ = f.__name__ + '({})'.format(
            ', '.join(itertools.chain(map(repr, args), ('{}={!r}'.format(k, v) for k, v in kwargs.items())))
        )
        return retval

    _transformation_factory._partial = True

    return _transformation_factory
