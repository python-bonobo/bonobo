import bonobo

graph = bonobo.Graph(
    bonobo.FileReader('coffeeshops.txt'),
    print,
)


def get_services():
    return {'fs': bonobo.open_examples_fs('datasets')}


if __name__ == '__main__':
    bonobo.run(graph, services=get_services())
