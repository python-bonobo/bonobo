import bonobo, json, unittest, time
from bonobo.execution import events
from bonobo.execution.contexts.graph import GraphExecutionContext
from bonobo.contrib.slack import SlackPlugin
from slackclient import SlackClient
from whistle import EventDispatcher
from unittest.mock import MagicMock, patch
from datetime import datetime as dt
from mock import *

time = Mock()
time.return_value = time.mktime(dt(2018, 3, 5, 17, 18, 47).timetuple())
time.strftime("%y/%m/%d %H:%M:%S").return_value = '18/05/03 17:18:47'

class SlackPluginTest(unittest.TestCase):

    def test_register_unregister(self):
        plugin = SlackPlugin(slack_api_token='123456', env='test', channel='test', name='test job')
        dispatcher = EventDispatcher()

        plugin.register(dispatcher)
        assert plugin.started in dispatcher.get_listeners(events.STARTED)
        assert plugin.stop in dispatcher.get_listeners(events.STOP)

        plugin.unregister(dispatcher)
        assert plugin.started not in dispatcher.get_listeners(events.STARTED)
        assert plugin.stop not in dispatcher.get_listeners(events.STOP)

    def test_one_pass(self):
        plugin = SlackPlugin(slack_api_token='123456', env='test', channel='test', name='test job')
        dispatcher = EventDispatcher()
        plugin.register(dispatcher)

        graph = bonobo.Graph()
        context = MagicMock(spec=GraphExecutionContext(graph))

        dispatcher.dispatch(events.STARTED, events.ExecutionEvent(context))
        dispatcher.dispatch(events.STOP, events.ExecutionEvent(context))

        plugin.unregister(dispatcher)

    @patch('bonobo.contrib.slack.time')
    @patch('bonobo.contrib.slack.datetime')
    def test_api_call_pass(self, mock_time, mock_datetime):

        mock_time.time = Mock(return_value= time.mktime(dt(2018, 3, 5, 12, 00, 00).timetuple()))
        mock_datetime.now = Mock(return_value='2018-03-05 12:00:00')

        print(mock_datetime.now())

        with patch.object(SlackClient, 'api_call') as slackClientMock:
            plugin = SlackPlugin(slack_api_token='123456', env='test', channel='test', name='test job')
            dispatcher = EventDispatcher()
            plugin.register(dispatcher)

            graph = bonobo.Graph()
            context = MagicMock(spec=GraphExecutionContext(graph))

            dispatcher.dispatch(events.STARTED, events.ExecutionEvent(context))
            dispatcher.dispatch(events.STOP, events.ExecutionEvent(context))

            plugin.unregister(dispatcher)

        slackClientMock.assert_called_once_with(
            'chat.postMessage',
            channel='test',
            text="Job {} triggered".format('test job'),
            attachments=json.dumps([
                {
                    "author_icon": "https://avatars3.githubusercontent.com/u/24471061?s=200&v=4",
                    "author_name": "Bonobo",
                    "author_link": "https://github.com/python-bonobo",
                    "color": "#7CD197",
                    "footer": "Triggered at 18/05/03 17:18:47. Completed in 1s",
                    "fields": [
                        {
                            "title": "Job",
                            "value": "test job",
                            "short": True
                        },
                        {
                            "title": "Environment",
                            "value": "test",
                            "short": True
                        }
                    ]
                }
            ]),
            username="Bonobo"
        )
