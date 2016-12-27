from bonobo.util import noop


def _create_lifecycle_functions(noun, verb):
    getter = lambda c: getattr(c, verb, noop)
    getter.__name__ = 'get_' + noun

    def setter(f):
        nonlocal noun, verb
        assert callable(f), 'You must provide a callable to decorate with {}.'.format(noun)

        def wrapper(c):
            nonlocal verb, f
            setattr(f, verb, c)
            return f

        return wrapper

    setter.__name__ = 'set_' + noun

    return getter, setter


get_initializer, set_initializer = _create_lifecycle_functions('initializer', 'initialize')
get_finalizer, set_finalizer = _create_lifecycle_functions('finalizer', 'finalize')


class Contextual:
    _with_context = True


def with_context(cls_or_func):
    cls_or_func._with_context = True
    return cls_or_func
