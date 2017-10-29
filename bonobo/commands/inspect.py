from bonobo.commands import BaseGraphCommand

OUTPUT_GRAPH = 'graphviz'


class InspectCommand(BaseGraphCommand):
    def add_arguments(self, parser):
        super(InspectCommand, self).add_arguments(parser)
        parser.add_argument('--graph', '-g', dest='output', action='store_const', const=OUTPUT_GRAPH)

    def handle(self, output=None, **options):
        if output is None:
            raise ValueError('Output type must be provided (try --graph/-g).')

        graph, params = self.read(**options)

        if output == OUTPUT_GRAPH:
            print(graph._repr_dot_())
        else:
            raise NotImplementedError('Output type not implemented.')

