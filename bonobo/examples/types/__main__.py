import bonobo
from bonobo.examples.types.strings import get_graph

if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser):
        bonobo.run(get_graph())
