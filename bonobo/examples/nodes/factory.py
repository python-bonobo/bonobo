from functools import partial

import itertools

import bonobo
from bonobo.commands.run import get_default_services
from bonobo.config import Configurable
from bonobo.nodes.factory import Factory
from bonobo.nodes.io.json import JsonDictReader


@Factory
def Normalize(self):
    self[0].str().title()
    self.move(0, 'title')
    self.move(0, 'address')


class PrettyPrinter(Configurable):
    def call(self, *args, **kwargs):
        for i, (
            item, value
        ) in enumerate(itertools.chain(enumerate(args), kwargs.items())):
            print('  ' if i else '• ', item, '=', value)


graph = bonobo.Graph(
    JsonDictReader('datasets/coffeeshops.json'),
    Normalize(),
    PrettyPrinter(),
)

if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__))
