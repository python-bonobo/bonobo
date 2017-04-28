import bonobo
from bonobo.commands.run import get_default_services

graph = bonobo.Graph(
    bonobo.FileReader(path='datasets/coffeeshops.txt'),
    print,
)


def get_services():
    return {'fs': bonobo.open_fs(bonobo.get_examples_path())}


if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__, get_services()))
