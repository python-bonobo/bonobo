from bonobo.util.python import require


def test_require():
    dummy = require('requireable.dummy')
    assert dummy.foo == 'bar'
