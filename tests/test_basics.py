import pprint
from unittest.mock import MagicMock

import bonobo
import pytest
from bonobo.config.processors import ContextCurrifier


def test_count():
    with pytest.raises(TypeError):
        bonobo.count()

    context = MagicMock()

    currified = ContextCurrifier(bonobo.count)
    currified.setup(context)

    for i in range(42):
        currified()
    currified.teardown()

    context.send.assert_called_once()
    bag = context.send.call_args[0][0]
    assert isinstance(bag, bonobo.Bag)
    assert 0 == len(bag.kwargs)
    assert 1 == len(bag.args)
    assert bag.args[0] == 42
