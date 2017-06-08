import bonobo
from bonobo import Bag
from bonobo.commands.run import get_default_services


def get_fields(**row):
    return Bag(**row['fields'])


graph = bonobo.Graph(
    bonobo.JsonReader('datasets/theaters.json'),
    get_fields,
    bonobo.PrettyPrinter(),
)

if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__))
