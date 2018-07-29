from bonobo.constants import NOT_MODIFIED
from bonobo.util.testing import BufferingNodeExecutionContext


def useless(*args, **kwargs):
    return NOT_MODIFIED


def test_not_modified():
    input_messages = [("foo", "bar"), ("foo", "baz")]

    with BufferingNodeExecutionContext(useless) as context:
        context.write_sync(*input_messages)

    result = context.get_buffer()
    print(result)
    assert result == input_messages
