from bonobo import CsvReader, Graph, get_examples_path

graph = Graph(
    CsvReader(path=get_examples_path('datasets/coffeeshops.txt')),
    print,
)

if __name__ == '__main__':
    import bonobo

    bonobo.run(graph)
