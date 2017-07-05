import bonobo

from bonobo import Filter


class OddOnlyFilter(Filter):
    def filter(self, i):
        return i % 2


@Filter
def multiples_of_three(i):
    return not (i % 3)


graph = bonobo.Graph(
    lambda: tuple(range(50)),
    OddOnlyFilter(),
    multiples_of_three,
    print,
)

if __name__ == '__main__':
    bonobo.run(graph)
