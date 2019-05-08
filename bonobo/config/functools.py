import functools
import itertools

from bonobo.config.services import use
from bonobo.util import get_name


def transformation_factory(f):
    @functools.wraps(f)
    def _transformation_factory(*args, **kwargs):
        retval = f(*args, **kwargs)
        retval.__name__ = f.__name__ + "({})".format(
            ", ".join(itertools.chain(map(repr, args), ("{}={!r}".format(k, v) for k, v in kwargs.items())))
        )
        return retval

    _transformation_factory._partial = True

    return _transformation_factory


class partial(functools.partial):
    @property
    def __name__(self):
        return get_name(self.func)

    def using(self, *service_names):
        return use(*service_names)(self)
