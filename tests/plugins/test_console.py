from unittest.mock import MagicMock

from whistle import EventDispatcher

import bonobo
from bonobo.execution import events
from bonobo.execution.contexts.graph import GraphExecutionContext
from bonobo.plugins.console import ConsoleOutputPlugin


def test_register_unregister():
    plugin = ConsoleOutputPlugin()
    dispatcher = EventDispatcher()

    plugin.register(dispatcher)
    assert plugin.setup in dispatcher.get_listeners(events.START)
    assert plugin.tick in dispatcher.get_listeners(events.TICK)
    assert plugin.teardown in dispatcher.get_listeners(events.STOPPED)
    plugin.unregister(dispatcher)
    assert plugin.setup not in dispatcher.get_listeners(events.START)
    assert plugin.tick not in dispatcher.get_listeners(events.TICK)
    assert plugin.teardown not in dispatcher.get_listeners(events.STOPPED)


def test_one_pass():
    plugin = ConsoleOutputPlugin()
    dispatcher = EventDispatcher()
    plugin.register(dispatcher)

    graph = bonobo.Graph()
    context = MagicMock(spec=GraphExecutionContext(graph))

    dispatcher.dispatch(events.START, events.ExecutionEvent(context))
    dispatcher.dispatch(events.TICK, events.ExecutionEvent(context))
    dispatcher.dispatch(events.STOPPED, events.ExecutionEvent(context))

    plugin.unregister(dispatcher)
