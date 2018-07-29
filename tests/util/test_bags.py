"""Those tests are mostly a copy paste of cpython unit tests for namedtuple, with a few differences to reflect the
implementation details that differs. It ensures that we caught the same edge cases as they did."""

import collections
import copy
import pickle
import string
import sys
import unittest
from collections import OrderedDict
from random import choice

from bonobo.util.bags import BagType

################################################################################
### Named Tuples
################################################################################

TBag = BagType("TBag", ("x", "y", "z"))  # type used for pickle tests


class TestBagType(unittest.TestCase):
    def _create(self, *fields, typename="abc"):
        bt = BagType(typename, fields)
        assert bt._fields == fields
        assert len(bt._fields) == len(bt._attrs)
        return bt

    def test_factory(self):
        Point = BagType("Point", ("x", "y"))
        self.assertEqual(Point.__name__, "Point")
        self.assertEqual(Point.__slots__, ())
        self.assertEqual(Point.__module__, __name__)
        self.assertEqual(Point.__getitem__, tuple.__getitem__)
        assert Point._fields == ("x", "y")
        assert Point._attrs == ("x", "y")

        self.assertRaises(ValueError, BagType, "abc%", ("efg", "ghi"))  # type has non-alpha char
        self.assertRaises(ValueError, BagType, "class", ("efg", "ghi"))  # type has keyword
        self.assertRaises(ValueError, BagType, "9abc", ("efg", "ghi"))  # type starts with digit

        assert self._create("efg", "g%hi")._attrs == ("efg", "g_hi")
        assert self._create("abc", "class")._attrs == ("abc", "_class")
        assert self._create("8efg", "9ghi")._attrs == ("_8efg", "_9ghi")
        assert self._create("_efg", "ghi")._attrs == ("_efg", "ghi")

        self.assertRaises(ValueError, BagType, "abc", ("efg", "efg", "ghi"))  # duplicate field

        self._create("x1", "y2", typename="Point0")  # Verify that numbers are allowed in names
        self._create("a", "b", "c", typename="_")  # Test leading underscores in a typename

        bt = self._create("a!", "a?")
        assert bt._attrs == ("a0", "a1")
        x = bt("foo", "bar")
        assert x.get("a!") == "foo"
        assert x.a0 == "foo"
        assert x.get("a?") == "bar"
        assert x.a1 == "bar"

        # check unicode output
        bt = self._create("the", "quick", "brown", "fox")
        assert "u'" not in repr(bt._fields)

        self.assertRaises(TypeError, Point._make, [11])  # catch too few args
        self.assertRaises(TypeError, Point._make, [11, 22, 33])  # catch too many args

    @unittest.skipIf(sys.flags.optimize >= 2, "Docstrings are omitted with -O2 and above")
    def test_factory_doc_attr(self):
        Point = BagType("Point", ("x", "y"))
        self.assertEqual(Point.__doc__, "Point(x, y)")

    @unittest.skipIf(sys.flags.optimize >= 2, "Docstrings are omitted with -O2 and above")
    def test_doc_writable(self):
        Point = BagType("Point", ("x", "y"))
        self.assertEqual(Point.x.__doc__, "Alias for 'x'")
        Point.x.__doc__ = "docstring for Point.x"
        self.assertEqual(Point.x.__doc__, "docstring for Point.x")

    def test_name_fixer(self):
        for spec, renamed in [
            [("efg", "g%hi"), ("efg", "g_hi")],  # field with non-alpha char
            [("abc", "class"), ("abc", "_class")],  # field has keyword
            [("8efg", "9ghi"), ("_8efg", "_9ghi")],  # field starts with digit
            [("abc", "_efg"), ("abc", "_efg")],  # field with leading underscore
            [("abc", "", "x"), ("abc", "_0", "x")],  # fieldname is a space
            [("&", "¨", "*"), ("_0", "_1", "_2")],  # Duplicate attrs, in theory
        ]:
            assert self._create(*spec)._attrs == renamed

    def test_module_parameter(self):
        NT = BagType("NT", ["x", "y"], module=collections)
        self.assertEqual(NT.__module__, collections)

    def test_instance(self):
        Point = self._create("x", "y", typename="Point")
        p = Point(11, 22)
        self.assertEqual(p, Point(x=11, y=22))
        self.assertEqual(p, Point(11, y=22))
        self.assertEqual(p, Point(y=22, x=11))
        self.assertEqual(p, Point(*(11, 22)))
        self.assertEqual(p, Point(**dict(x=11, y=22)))
        self.assertRaises(TypeError, Point, 1)  # too few args
        self.assertRaises(TypeError, Point, 1, 2, 3)  # too many args
        self.assertRaises(TypeError, eval, "Point(XXX=1, y=2)", locals())  # wrong keyword argument
        self.assertRaises(TypeError, eval, "Point(x=1)", locals())  # missing keyword argument
        self.assertEqual(repr(p), "Point(x=11, y=22)")
        self.assertNotIn("__weakref__", dir(p))
        self.assertEqual(p, Point._make([11, 22]))  # test _make classmethod
        self.assertEqual(p._fields, ("x", "y"))  # test _fields attribute
        self.assertEqual(p._replace(x=1), (1, 22))  # test _replace method
        self.assertEqual(p._asdict(), dict(x=11, y=22))  # test _asdict method

        try:
            p._replace(x=1, error=2)
        except ValueError:
            pass
        else:
            self._fail("Did not detect an incorrect fieldname")

        p = Point(x=11, y=22)
        self.assertEqual(repr(p), "Point(x=11, y=22)")

    def test_tupleness(self):
        Point = BagType("Point", ("x", "y"))
        p = Point(11, 22)

        self.assertIsInstance(p, tuple)
        self.assertEqual(p, (11, 22))  # matches a real tuple
        self.assertEqual(tuple(p), (11, 22))  # coercable to a real tuple
        self.assertEqual(list(p), [11, 22])  # coercable to a list
        self.assertEqual(max(p), 22)  # iterable
        self.assertEqual(max(*p), 22)  # star-able
        x, y = p
        self.assertEqual(p, (x, y))  # unpacks like a tuple
        self.assertEqual((p[0], p[1]), (11, 22))  # indexable like a tuple
        self.assertRaises(IndexError, p.__getitem__, 3)

        self.assertEqual(p.x, x)
        self.assertEqual(p.y, y)
        self.assertRaises(AttributeError, eval, "p.z", locals())

    def test_odd_sizes(self):
        Zero = BagType("Zero", ())
        self.assertEqual(Zero(), ())
        self.assertEqual(Zero._make([]), ())
        self.assertEqual(repr(Zero()), "Zero()")
        self.assertEqual(Zero()._asdict(), {})
        self.assertEqual(Zero()._fields, ())

        Dot = BagType("Dot", ("d",))
        self.assertEqual(Dot(1), (1,))
        self.assertEqual(Dot._make([1]), (1,))
        self.assertEqual(Dot(1).d, 1)
        self.assertEqual(repr(Dot(1)), "Dot(d=1)")
        self.assertEqual(Dot(1)._asdict(), {"d": 1})
        self.assertEqual(Dot(1)._replace(d=999), (999,))
        self.assertEqual(Dot(1)._fields, ("d",))

        n = 5000 if sys.version_info >= (3, 7) else 254
        names = list(set("".join([choice(string.ascii_letters) for j in range(10)]) for i in range(n)))
        n = len(names)
        Big = BagType("Big", names)
        b = Big(*range(n))
        self.assertEqual(b, tuple(range(n)))
        self.assertEqual(Big._make(range(n)), tuple(range(n)))
        for pos, name in enumerate(names):
            self.assertEqual(getattr(b, name), pos)
        repr(b)  # make sure repr() doesn't blow-up
        d = b._asdict()
        d_expected = dict(zip(names, range(n)))
        self.assertEqual(d, d_expected)
        b2 = b._replace(**dict([(names[1], 999), (names[-5], 42)]))
        b2_expected = list(range(n))
        b2_expected[1] = 999
        b2_expected[-5] = 42
        self.assertEqual(b2, tuple(b2_expected))
        self.assertEqual(b._fields, tuple(names))

    def test_pickle(self):
        p = TBag(x=10, y=20, z=30)
        for module in (pickle,):
            loads = getattr(module, "loads")
            dumps = getattr(module, "dumps")
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                q = loads(dumps(p, protocol))
                self.assertEqual(p, q)
                self.assertEqual(p._fields, q._fields)
                self.assertNotIn(b"OrderedDict", dumps(p, protocol))

    def test_copy(self):
        p = TBag(x=10, y=20, z=30)
        for copier in copy.copy, copy.deepcopy:
            q = copier(p)
            self.assertEqual(p, q)
            self.assertEqual(p._fields, q._fields)

    def test_name_conflicts(self):
        # Some names like "self", "cls", "tuple", "itemgetter", and "property"
        # failed when used as field names.  Test to make sure these now work.
        T = BagType("T", ("itemgetter", "property", "self", "cls", "tuple"))
        t = T(1, 2, 3, 4, 5)
        self.assertEqual(t, (1, 2, 3, 4, 5))
        newt = t._replace(itemgetter=10, property=20, self=30, cls=40, tuple=50)
        self.assertEqual(newt, (10, 20, 30, 40, 50))

        # Broader test of all interesting names taken from the code, old
        # template, and an example
        words = {
            "Alias",
            "At",
            "AttributeError",
            "Build",
            "Bypass",
            "Create",
            "Encountered",
            "Expected",
            "Field",
            "For",
            "Got",
            "Helper",
            "IronPython",
            "Jython",
            "KeyError",
            "Make",
            "Modify",
            "Note",
            "OrderedDict",
            "Point",
            "Return",
            "Returns",
            "Type",
            "TypeError",
            "Used",
            "Validate",
            "ValueError",
            "Variables",
            "a",
            "accessible",
            "add",
            "added",
            "all",
            "also",
            "an",
            "arg_list",
            "args",
            "arguments",
            "automatically",
            "be",
            "build",
            "builtins",
            "but",
            "by",
            "cannot",
            "class_namespace",
            "classmethod",
            "cls",
            "collections",
            "convert",
            "copy",
            "created",
            "creation",
            "d",
            "debugging",
            "defined",
            "dict",
            "dictionary",
            "doc",
            "docstring",
            "docstrings",
            "duplicate",
            "effect",
            "either",
            "enumerate",
            "environments",
            "error",
            "example",
            "exec",
            "f",
            "f_globals",
            "field",
            "field_names",
            "fields",
            "formatted",
            "frame",
            "function",
            "functions",
            "generate",
            "getter",
            "got",
            "greater",
            "has",
            "help",
            "identifiers",
            "indexable",
            "instance",
            "instantiate",
            "interning",
            "introspection",
            "isidentifier",
            "isinstance",
            "itemgetter",
            "iterable",
            "join",
            "keyword",
            "keywords",
            "kwds",
            "len",
            "like",
            "list",
            "map",
            "maps",
            "message",
            "metadata",
            "method",
            "methods",
            "module",
            "module_name",
            "must",
            "name",
            "named",
            "namedtuple",
            "namedtuple_",
            "names",
            "namespace",
            "needs",
            "new",
            "nicely",
            "num_fields",
            "number",
            "object",
            "of",
            "operator",
            "option",
            "p",
            "particular",
            "pickle",
            "pickling",
            "plain",
            "pop",
            "positional",
            "property",
            "r",
            "regular",
            "rename",
            "replace",
            "replacing",
            "repr",
            "repr_fmt",
            "representation",
            "result",
            "reuse_itemgetter",
            "s",
            "seen",
            "sequence",
            "set",
            "side",
            "specified",
            "split",
            "start",
            "startswith",
            "step",
            "str",
            "string",
            "strings",
            "subclass",
            "sys",
            "targets",
            "than",
            "the",
            "their",
            "this",
            "to",
            "tuple_new",
            "type",
            "typename",
            "underscore",
            "unexpected",
            "unpack",
            "up",
            "use",
            "used",
            "user",
            "valid",
            "values",
            "variable",
            "verbose",
            "where",
            "which",
            "work",
            "x",
            "y",
            "z",
            "zip",
        }
        sorted_words = tuple(sorted(words))
        T = BagType("T", sorted_words)
        # test __new__
        values = tuple(range(len(words)))
        t = T(*values)
        self.assertEqual(t, values)
        t = T(**dict(zip(T._attrs, values)))
        self.assertEqual(t, values)
        # test _make
        t = T._make(values)
        self.assertEqual(t, values)
        # exercise __repr__
        repr(t)
        # test _asdict
        self.assertEqual(t._asdict(), dict(zip(T._fields, values)))
        # test _replace
        t = T._make(values)
        newvalues = tuple(v * 10 for v in values)
        newt = t._replace(**dict(zip(T._fields, newvalues)))
        self.assertEqual(newt, newvalues)
        # test _fields
        self.assertEqual(T._attrs, sorted_words)
        # test __getnewargs__
        self.assertEqual(t.__getnewargs__(), values)

    def test_repr(self):
        A = BagType("A", ("x",))
        self.assertEqual(repr(A(1)), "A(x=1)")

        # repr should show the name of the subclass
        class B(A):
            pass

        self.assertEqual(repr(B(1)), "B(x=1)")

    def test_namedtuple_subclass_issue_24931(self):
        class Point(BagType("_Point", ["x", "y"])):
            pass

        a = Point(3, 4)
        self.assertEqual(a._asdict(), OrderedDict([("x", 3), ("y", 4)]))

        a.w = 5
        self.assertEqual(a.__dict__, {"w": 5})

    def test_annoying_attribute_names(self):
        self._create(
            "__slots__",
            "__getattr__",
            "_attrs",
            "_fields",
            "__new__",
            "__getnewargs__",
            "__repr__",
            "_make",
            "get",
            "_replace",
            "_asdict",
            "_cls",
            "self",
            "tuple",
        )
