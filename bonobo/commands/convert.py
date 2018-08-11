import bonobo
from bonobo.commands import BaseCommand
from bonobo.registry import READER, WRITER, default_registry
from bonobo.util.resolvers import _resolve_options, _resolve_transformations


class ConvertCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('input_filename', help='Input filename.')
        parser.add_argument('output_filename', help='Output filename.')
        parser.add_argument(
            '--' + READER,
            '-r',
            help='Choose the reader factory if it cannot be detected from extension, or if detection is wrong.',
        )
        parser.add_argument(
            '--' + WRITER,
            '-w',
            help='Choose the writer factory if it cannot be detected from extension, or if detection is wrong (use - for console pretty print).',
        )
        parser.add_argument('--limit', '-l', type=int, help='Adds a Limit() after the reader instance.', default=None)
        parser.add_argument(
            '--transformation',
            '-t',
            dest='transformation',
            action='append',
            help='Add a transformation between input and output (can be used multiple times, order is preserved).',
        )
        parser.add_argument(
            '--option',
            '-O',
            dest='option',
            action='append',
            help='Add a named option to both reader and writer factories (i.e. foo="bar").',
        )
        parser.add_argument(
            '--' + READER + '-option',
            '-' + READER[0].upper(),
            dest=READER + '_option',
            action='append',
            help='Add a named option to the reader factory.',
        )
        parser.add_argument(
            '--' + WRITER + '-option',
            '-' + WRITER[0].upper(),
            dest=WRITER + '_option',
            action='append',
            help='Add a named option to the writer factory.',
        )

    def handle(
        self,
        input_filename,
        output_filename,
        reader=None,
        reader_option=None,
        writer=None,
        writer_option=None,
        option=None,
        limit=None,
        transformation=None,
    ):
        reader_factory = default_registry.get_reader_factory_for(input_filename, format=reader)
        reader_kwargs = _resolve_options((option or []) + (reader_option or []))

        if output_filename == '-':
            writer_factory = bonobo.PrettyPrinter
            writer_args = ()
        else:
            writer_factory = default_registry.get_writer_factory_for(output_filename, format=writer)
            writer_args = (output_filename,)
        writer_kwargs = _resolve_options((option or []) + (writer_option or []))

        transformations = ()

        if limit:
            transformations += (bonobo.Limit(limit),)

        transformations += _resolve_transformations(transformation)

        graph = bonobo.Graph()
        graph.add_chain(
            reader_factory(input_filename, **reader_kwargs),
            *transformations,
            writer_factory(*writer_args, **writer_kwargs),
        )

        return bonobo.run(graph, services={'fs': bonobo.open_fs()})
