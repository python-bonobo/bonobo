""" Various simple utilities. """

import functools
from pprint import pprint as _pprint

import blessings

from .helpers import run, console_run, jupyter_run
from .tokens import NOT_MODIFIED

__all__ = [
    'NOT_MODIFIED',
    'console_run',
    'jupyter_run',
    'limit',
    'log',
    'noop',
    'pprint',
    'run',
    'tee',
]


def identity(x):
    return x


def limit(n=10):
    i = 0

    def _limit(*args, **kwargs):
        nonlocal i, n
        i += 1
        if i <= n:
            yield NOT_MODIFIED

    _limit.__name__ = 'limit({})'.format(n)
    return _limit


def tee(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        nonlocal f
        f(*args, **kwargs)
        return NOT_MODIFIED

    return wrapped


log = tee(_pprint)


def pprint(title_keys=('title', 'name', 'id'), print_values=True, sort=True):
    term = blessings.Terminal()

    def _pprint(*args, **kwargs):
        nonlocal title_keys, term, sort, print_values

        row = args[0]
        for key in title_keys:
            if key in row:
                print(term.bold(row.get(key)))
                break

        if print_values:
            for k in sorted(row) if sort else row:
                print(
                    '  • {t.blue}{k}{t.normal} : {t.black}({tp}){t.normal} {v}{t.clear_eol}'.format(
                        k=k, v=repr(row[k]), t=term, tp=type(row[k]).__name__
                    )
                )

        yield NOT_MODIFIED

    _pprint.__name__ = 'pprint'

    return _pprint


'''

    def writehr(self, label=None):
        width = t.width or 80

        if label:
            label = str(label)
            sys.stderr.write(t.black('·' * 4) + shade('{') + label + shade('}') + t.black('·' * (width - (6+len(label)) - 1)) + '\n')
        else:
            sys.stderr.write(t.black('·' * (width-1) + '\n'))


    def writeln(self, s):
        """Output method."""
        sys.stderr.write(self.format(s) + '\n')

    def initialize(self):
        self.lineno = 0

    def transform(self, hash, channel=STDIN):
        """Actual transformation."""
        self.lineno += 1
        if not self.condition or self.condition(hash):
            hash = hash.copy()
            hash = hash if not isinstance(self.field_filter, collections.Callable) else hash.restrict(self.field_filter)
            if self.clean:
                hash = hash.restrict(lambda k: len(k) and k[0] != '_')
            self.writehr(self.lineno)
            self.writeln(hash)
            self.writehr()
            sys.stderr.write('\n')
        yield hash
'''


def noop(*args, **kwargs):  # pylint: disable=unused-argument
    pass
