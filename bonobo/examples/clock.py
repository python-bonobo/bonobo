import datetime
import time

import bonobo


def extract():
    """Placeholder, change, rename, remove... """
    for x in range(60):
        if x:
            time.sleep(1)
        yield datetime.datetime.now()


def get_graph():
    graph = bonobo.Graph()
    graph.add_chain(extract, print)

    return graph


if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser):
        bonobo.run(get_graph())
