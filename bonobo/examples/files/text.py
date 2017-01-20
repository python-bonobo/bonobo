from bonobo import FileReader, Graph


def skip_comments(line):
    if not line.startswith('#'):
        yield line


graph = Graph(
    FileReader(path='/etc/passwd'),
    skip_comments,
    lambda s: s.split(':'),
    lambda l: l[0],
    print,
)

if __name__ == '__main__':
    import bonobo

    bonobo.run(graph)
