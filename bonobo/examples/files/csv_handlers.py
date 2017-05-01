import bonobo
from bonobo.commands.run import get_default_services

graph = bonobo.Graph(
    bonobo.CsvReader('datasets/coffeeshops.txt'),
    print,
)

if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__))
