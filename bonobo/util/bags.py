import functools
import re
import sys
from keyword import iskeyword

from slugify import slugify

_class_template = '''\
from builtins import property as _property, tuple as _tuple
from operator import itemgetter as _itemgetter
from collections import OrderedDict

class {typename}(tuple):
    '{typename}({arg_list})'

    __slots__ = ()
    _attrs = {attrs!r}
    _fields = {fields!r}
    
    def __new__(_cls, {arg_list}):
        """
        Create new instance of {typename}({arg_list})
        
        """
        return _tuple.__new__(_cls, ({arg_list}))
        
    def __getnewargs__(self):
        """
        Return self as a plain tuple.
        Used by copy and pickle.
        
        """
        return tuple(self)
        
    def __repr__(self):
        """
        Return a nicely formatted representation string
        
        """
        return self.__class__.__name__ + '({repr_fmt})' % self
        
    def get(self, field, default=None):
        try:
            index = self._fields.index(field)
        except ValueError:
            return default
        return self[index]
        
    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new {typename} object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != {num_fields:d}:
            raise TypeError('Expected {num_fields:d} arguments, got %d' % len(result))
        return result
        
    def _replace(_self, **kwds):
        'Return a new {typename} object replacing specified fields with new values'
        result = _self._make(map(kwds.pop, {fields!r}, _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % list(kwds))
        return result
        
    def _asdict(self):
        """
        Return a new OrderedDict which maps field names to their values.
        
        """
        return OrderedDict(zip(self._fields, self))
        
{field_defs}
'''

_field_template = '''\
    {name} = _property(_itemgetter({index:d}), doc={doc!r})
'''.strip(
    '\n'
)

_reserved = frozenset(
    ['_', '_cls', '_attrs', '_fields', 'get', '_asdict', '_replace', '_make', 'self', '_self', 'tuple'] + dir(tuple)
)

_multiple_underscores_pattern = re.compile('__+')
_slugify_allowed_chars_pattern = re.compile(r'[^a-z0-9_]+', flags=re.IGNORECASE)


def _uniquify(f):
    seen = set(_reserved)

    @functools.wraps(f)
    def _uniquified(x):
        nonlocal f, seen
        x = str(x)
        v = v0 = _multiple_underscores_pattern.sub('_', f(x))
        i = 0
        # if last character is not "allowed", let's start appending indexes right from the first iteration
        if len(x) and _slugify_allowed_chars_pattern.match(x[-1]):
            v = '{}{}'.format(v0, i)
        while v in seen:
            v = '{}{}'.format(v0, i)
            i += 1
        seen.add(v)
        return v

    return _uniquified


def _make_valid_attr_name(x):
    if iskeyword(x):
        x = '_' + x
    if x.isidentifier():
        return x
    x = slugify(x, separator='_', regex_pattern=_slugify_allowed_chars_pattern)
    if x.isidentifier():
        return x
    x = '_' + x
    if x.isidentifier():
        return x
    raise ValueError(x)


def BagType(typename, fields, *, verbose=False, module=None):
    # Validate the field names.  At the user's option, either generate an error
    # message or automatically replace the field name with a valid name.

    attrs = tuple(map(_uniquify(_make_valid_attr_name), fields))
    if isinstance(fields, str):
        raise TypeError('BagType does not support providing fields as a string.')
    fields = list(map(str, fields))
    typename = str(typename)

    for i, name in enumerate([typename] + fields):
        if not isinstance(name, str):
            raise TypeError('Type names and field names must be strings, got {name!r}'.format(name=name))
        if not i:
            if not name.isidentifier():
                raise ValueError('Type names must be valid identifiers: {name!r}'.format(name=name))
            if iskeyword(name):
                raise ValueError('Type names cannot be a keyword: {name!r}'.format(name=name))

    seen = set()
    for name in fields:
        if name in seen:
            raise ValueError('Encountered duplicate field name: {name!r}'.format(name=name))
        seen.add(name)

    # Fill-in the class template
    class_definition = _class_template.format(
        typename=typename,
        fields=tuple(fields),
        attrs=attrs,
        num_fields=len(fields),
        arg_list=repr(attrs).replace("'", "")[1:-1],
        repr_fmt=', '.join(
            ('%r' if isinstance(fields[index], int) else '{name}=%r').format(name=name)
            for index, name in enumerate(attrs)
        ),
        field_defs='\n'.join(
            _field_template.format(
                index=index,
                name=name,
                doc='Alias for '
                + ('field #{}'.format(index) if isinstance(fields[index], int) else repr(fields[index])),
            )
            for index, name in enumerate(attrs)
        ),
    )

    # Execute the template string in a temporary namespace and support
    # tracing utilities by setting a value for frame.f_globals['__name__']
    namespace = dict(__name__='namedtuple_%s' % typename)
    exec(class_definition, namespace)
    result = namespace[typename]
    result._source = class_definition
    if verbose:
        print(result._source)

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in environments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython), or where the user has
    # specified a particular module.
    if module is None:
        try:
            module = sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
    if module is not None:
        result.__module__ = module

    return result
