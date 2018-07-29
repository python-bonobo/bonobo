from collections import namedtuple
from typing import Callable

import pytest

from bonobo.constants import EMPTY
from bonobo.util.bags import BagType
from bonobo.util.envelopes import Envelope
from bonobo.util.testing import BufferingNodeExecutionContext

MyTuple = namedtuple("MyTuple", ["a", "b", "c"])
MyBag = BagType("MyBag", ["a", "b", "c"])


class MyCustomType:
    def __init__(self, *args):
        self.args = args

    def as_tuple(self):
        return MyBag(*self.args)


@pytest.mark.parametrize(
    ["factory", "expected", "expected_item0"],
    [
        [lambda: (1, 2, 3), tuple, int],
        [lambda: Envelope((1, 2, 3)), tuple, int],
        [lambda: MyTuple(1, 2, 3), MyTuple, int],
        [lambda: Envelope(MyTuple(1, 2, 3)), MyTuple, int],
        [lambda: MyBag(1, 2, 3), MyBag, int],
        [lambda: Envelope(MyBag(1, 2, 3)), MyBag, int],
        [lambda: MyCustomType(1, 2, 3), tuple, MyCustomType],
        [lambda: Envelope(MyCustomType(1, 2, 3)), tuple, MyCustomType],
    ],
)
def test_casts_after_output(factory: Callable, expected, expected_item0):
    def transform():
        yield factory()
        yield factory()

    with BufferingNodeExecutionContext(transform) as context:
        context.write_sync(EMPTY)

    result = context.get_buffer()
    assert expected == type(result[0])
    assert expected_item0 == type(result[0][0])
    assert expected == type(result[1])
    assert expected_item0 == type(result[1][0])


def test_cast_after_returning_custom_type():
    def transform():
        yield MyCustomType(1, 2, 3)
        yield MyCustomType(4, 5, 6)

    with BufferingNodeExecutionContext(transform) as context:
        context.write_sync(EMPTY)
    result = context.get_buffer()
    assert tuple == type(result[0])
    assert tuple == type(result[1])
    assert MyCustomType == type(result[0][0])
    assert MyCustomType == type(result[1][0])

    with BufferingNodeExecutionContext(MyCustomType.as_tuple) as context:
        context.write_sync(*result)
    result = context.get_buffer()
    assert MyBag == type(result[0])
    assert MyBag == type(result[1])
