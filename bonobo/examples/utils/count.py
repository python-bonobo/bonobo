import bonobo

graph = bonobo.Graph(range(42), bonobo.count, print)

if __name__ == '__main__':
    bonobo.run(graph)
