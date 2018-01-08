import bonobo


def split_one(line):
    return dict(zip(("name", "address"), line.split(', ', 1)))


graph = bonobo.Graph(
    bonobo.FileReader('coffeeshops.txt'),
    split_one,
    bonobo.JsonWriter('coffeeshops.json', fs='fs.output'),
)


def get_services():
    return {
        'fs': bonobo.open_examples_fs('datasets'),
        'fs.output': bonobo.open_fs(),
    }


if __name__ == '__main__':
    bonobo.run(graph, services=get_services())
