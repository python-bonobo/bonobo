import bonobo

graph = bonobo.Graph(
    bonobo.FileReader('coffeeshops.txt'),
    print,
)

if __name__ == '__main__':
    bonobo.run(
        graph, services={'fs': bonobo.open_examples_fs('datasets')}
    )
