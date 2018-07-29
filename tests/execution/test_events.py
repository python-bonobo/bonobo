from unittest.mock import Mock

from bonobo.execution import events


def test_names():
    # This test looks useless, but as it's becoming the pliugin API, I want to make sure that nothing changes here, or
    # notice it otherwise.
    for name in "start", "started", "tick", "stop", "stopped", "kill":
        event_name = getattr(events, name.upper())
        assert event_name == ".".join(("execution", name))


def test_event_object():
    # Same logic as above.
    c = Mock()
    e = events.ExecutionEvent(c)
    assert e.context is c
