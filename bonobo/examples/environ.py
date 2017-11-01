"""
This transformation extracts the environment and prints it, sorted alphabetically, one item per line.

Used in the bonobo tests around environment management.

"""
import os

import bonobo


def extract_environ():
    """Yield all the system environment."""
    yield from sorted(os.environ.items())


def get_graph():
    graph = bonobo.Graph()
    graph.add_chain(extract_environ, print)

    return graph


if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser):
        bonobo.run(get_graph())
