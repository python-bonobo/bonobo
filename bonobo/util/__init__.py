# Copyright 2012-2017 Romain Dorgueil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" bonobo.util
    ===========

    TODO
"""

import functools
import pprint

from .tokens import NotModified

__all__ = [
    'NotModified',
    'head',
    'log',
    'noop',
    'tee',
]


def head(n=10):
    i = 0

    def _head(x):
        nonlocal i, n
        i += 1
        if i <= n:
            yield x

    _head.__name__ = 'head({})'.format(n)
    return _head


def tee(f):
    @functools.wraps(f)
    def wrapped(x):
        nonlocal f
        f(x)
        return x

    return wrapped


log = tee(pprint.pprint)


def noop(*args, **kwargs):
    pass
