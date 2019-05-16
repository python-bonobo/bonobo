"""
The Util API, located under the :mod:`bonobo.util` namespace, contains helpers functions and decorators to work with
and inspect transformations, graphs, and nodes.

"""
from bonobo.util.collections import cast, ensure_tuple, sortedlist, tuplize
from bonobo.util.compat import deprecated, deprecated_alias
from bonobo.util.inspect import (
    inspect_node, isconfigurable, isconfigurabletype, iscontextprocessor, isdict, ismethod, isoption, istuple, istype
)
from bonobo.util.objects import ValueHolder, get_attribute_or_create, get_name

# Bonobo's util API
__all__ = [
    'ValueHolder',
    'cast',
    'deprecated',
    'deprecated_alias',
    'ensure_tuple',
    'get_attribute_or_create',
    'get_name',
    'inspect_node',
    'isconfigurable',
    'isconfigurabletype',
    'iscontextprocessor',
    'isdict',
    'ismethod',
    'isoption',
    'istype',
    'sortedlist',
    'tuplize',
]
