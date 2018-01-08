import bonobo
from bonobo.commands import BaseGraphCommand


class InspectCommand(BaseGraphCommand):
    handler = staticmethod(bonobo.inspect)

    def add_arguments(self, parser):
        super(InspectCommand, self).add_arguments(parser)
        parser.add_argument('--graph', '-g', dest='format', action='store_const', const='graph')

    def parse_options(self, **options):
        if not options.get('format'):
            raise RuntimeError('You must provide a format (try --graph).')
        return options
