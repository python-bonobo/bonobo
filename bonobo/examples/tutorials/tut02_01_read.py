import bonobo

graph = bonobo.Graph(
    bonobo.FileReader(path=bonobo.get_examples_path('datasets/coffeeshops.txt')),
    print,
)

if __name__ == '__main__':
    bonobo.run(graph)
