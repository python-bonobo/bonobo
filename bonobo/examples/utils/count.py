import bonobo
import bonobo.basics

graph = bonobo.Graph(range(42), bonobo.basics.count, print)

if __name__ == '__main__':
    bonobo.run(graph)
