from unittest.mock import MagicMock

import bonobo
from bonobo.execution import events
from bonobo.execution.contexts.graph import GraphExecutionContext
from bonobo.contrib.slack import SlackPlugin
from whistle import EventDispatcher

def test_register_unregister():
    plugin = SlackPlugin(slack_api_token='123456', env='test', channel='test', name='test job')
    dispatcher = EventDispatcher()

    plugin.register(dispatcher)
    assert plugin.started in dispatcher.get_listeners(events.STARTED)
    assert plugin.stop in dispatcher.get_listeners(events.STOP)

    plugin.unregister(dispatcher)
    assert plugin.started not in dispatcher.get_listeners(events.STARTED)
    assert plugin.stop not in dispatcher.get_listeners(events.STOP)

def test_one_pass():
    plugin = SlackPlugin(slack_api_token='123456', env='test', channel='test', name='test job')
    dispatcher = EventDispatcher()
    plugin.register(dispatcher)

    graph = bonobo.Graph()
    context = MagicMock(spec=GraphExecutionContext(graph))

    dispatcher.dispatch(events.STARTED, events.ExecutionEvent(context))
    dispatcher.dispatch(events.STOP, events.ExecutionEvent(context))

    plugin.unregister(dispatcher)
