import bonobo


def split_one(line):
    return line.split(', ', 1)


graph = bonobo.Graph(
    bonobo.FileReader(path='coffeeshops.txt'),
    split_one,
    bonobo.JsonWriter(path='coffeeshops.json'),
)

if __name__ == '__main__':
    bonobo.run(
        graph, services={'fs': bonobo.open_examples_fs('datasets')}
    )
