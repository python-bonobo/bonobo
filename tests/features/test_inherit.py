from bonobo.util.envelopes import AppendingEnvelope
from bonobo.util.testing import BufferingNodeExecutionContext

messages = [("Hello",), ("Goodbye",)]


def append(*args):
    return AppendingEnvelope("!")


def test_inherit():
    with BufferingNodeExecutionContext(append) as context:
        context.write_sync(*messages)

    assert context.get_buffer() == list(map(lambda x: x + ("!",), messages))


def test_inherit_bag_tuple():
    with BufferingNodeExecutionContext(append) as context:
        context.set_input_fields(["message"])
        context.write_sync(*messages)

    assert context.get_output_fields() == ("message", "0")
    assert context.get_buffer() == list(map(lambda x: x + ("!",), messages))
