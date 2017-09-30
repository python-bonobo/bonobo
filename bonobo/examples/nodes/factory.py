import bonobo
from bonobo.commands.run import get_default_services
from bonobo.nodes.factory import Factory
from bonobo.nodes.io.json import JsonDictItemsReader

normalize = Factory()
normalize[0].str().title()
normalize.move(0, 'title')
normalize.move(0, 'address')

graph = bonobo.Graph(
    JsonDictItemsReader('datasets/coffeeshops.json'),
    normalize,
    bonobo.PrettyPrinter(),
)

if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__))
