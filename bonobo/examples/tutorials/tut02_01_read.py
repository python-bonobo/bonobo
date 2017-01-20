import os
import pathlib

import bonobo

workdir = pathlib.Path(os.path.dirname(__file__))

graph = bonobo.Graph(
    bonobo.FileReader(path=workdir.joinpath('datasets/coffeeshops.txt')),
    print,
)

if __name__ == '__main__':
    bonobo.run(graph)
