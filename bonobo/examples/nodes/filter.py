import bonobo

from bonobo import Filter


class OddOnlyFilter(Filter):
    def filter(self, i):
        return i % 2


@Filter
def MultiplesOfThreeOnlyFilter(self, i):
    return not (i % 3)


graph = bonobo.Graph(
    lambda: tuple(range(50)),
    OddOnlyFilter(),
    MultiplesOfThreeOnlyFilter(),
    print,
)
