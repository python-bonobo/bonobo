from slackclient import SlackClient
from bonobo.plugins import Plugin
from bonobo.execution import events
from math import ceil
from time import time
import datetime
import json

class SlackPlugin(Plugin):
    def __init__(
            self,
            slack_api_token: str,
            env: str,
            channel: str,
            name: str,
            start_message: str = 'Start job {}',
            ok_color: str = '#7CD197',
            error_color: str = '#F35A00',
            report_only_failure: bool = False
    ):
        self.channel = channel
        self.client = SlackClient(slack_api_token)
        self.name = name
        self.start_message = start_message
        self.ok_color = ok_color
        self.error_color = error_color
        self.env = env
        self.triggered_at = None
        self.report_only_failure = report_only_failure

    def register(self, dispatcher):
        dispatcher.add_listener(events.STARTED, self.started)
        dispatcher.add_listener(events.STOP, self.stop)

    def unregister(self, dispatcher):
        dispatcher.remove_listener(events.STARTED, self.started)
        dispatcher.remove_listener(events.STOP, self.stop)

    def started(self, event):
        self.begin = time()
        self.triggered_at = datetime.datetime.now()

    def stop(self, event):
        duration_in_sec = ceil(time() - self.begin)
        stats = {}
        has_error = False

        for i in event.context.graph.topologically_sorted_indexes:
            node = event.context[i]
            node_name = node.name

            stats[node_name] = {}

            for idx, element in enumerate(node.get_statistics()):
                stats[node_name][element[0]] = element[1]

                if element[0] == 'err' and element[1] > 0:
                    has_error = True

        if self.report_only_failure and not has_error:
            return

        attachments  = {
            "author_icon": "https://avatars3.githubusercontent.com/u/24471061?s=200&v=4",
            "author_name": "Bonobo",
            "author_link": "https://github.com/python-bonobo",
            "color": self.error_color if True == has_error else self.ok_color,
            "footer": "Triggered at {}. Completed in {}s".format(self.triggered_at.strftime("%y/%m/%d %H:%M:%S"), duration_in_sec),
            "fields": [
                {
                    "title": "Job",
                    "value": self.name,
                    "short": True
                },
                {
                    "title": "Environment",
                    "value": self.env,
                    "short": True
                }
            ]
        }

        for graphName, stat in stats.items():
            message = 'In: '+ str(stat['in']) +'\n' if 'in' in stat else ''
            message += 'Out: '+ str(stat['out']) +'\n' if 'out' in stat else ''
            message += 'Warn: '+ str(stat['warn']) +'\n' if 'warn' in stat else ''
            message += 'Err: '+ str(stat['err']) +'\n' if 'err' in stat else ''

            attachments['fields'].append({
                "title": 'Graph Node : ' + graphName,
                "value": message,
                "short": True
            })

        self.client.api_call(
            'chat.postMessage',
            channel=self.channel,
            text="Job {} triggered".format(self.name),
            attachments=json.dumps([attachments]),
            username="Bonobo"
        )
