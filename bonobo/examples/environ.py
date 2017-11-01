import os

import bonobo


def extract_environ():
    yield from sorted(os.environ.items())


def get_graph():
    """
    This function builds the graph that needs to be executed.

    :return: bonobo.Graph

    """
    graph = bonobo.Graph()
    graph.add_chain(extract_environ, print)

    return graph


# The __main__ block actually execute the graph.
if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    parser.add_argument('-v', action='append', dest='vars')
    with bonobo.parse_args(parser):
        bonobo.run(get_graph())
