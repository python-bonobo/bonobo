import mimetypes
import os

import bonobo
from bonobo.commands.util.arguments import parse_variable_argument
from bonobo.util import require
from bonobo.util.iterators import tuplize
from bonobo.util.python import WorkingDirectoryModulesRegistry

SHORTCUTS = {
    'csv': 'text/csv',
    'json': 'application/json',
    'pickle': 'pickle',
    'plain': 'text/plain',
    'text': 'text/plain',
    'txt': 'text/plain',
}

REGISTRY = {
    'application/json': (bonobo.JsonReader, bonobo.JsonWriter),
    'pickle': (bonobo.PickleReader, bonobo.PickleWriter),
    'text/csv': (bonobo.CsvReader, bonobo.CsvWriter),
    'text/plain': (bonobo.FileReader, bonobo.FileWriter),
}

READER = 'reader'
WRITER = 'writer'


def resolve_factory(name, filename, factory_type, options=None):
    """
    Try to resolve which transformation factory to use for this filename. User eventually provided a name, which has
    priority, otherwise we try to detect it using the mimetype detection on filename.

    """
    if name is None:
        name = mimetypes.guess_type(filename)[0]

    if name in SHORTCUTS:
        name = SHORTCUTS[name]

    if name is None:
        _, _ext = os.path.splitext(filename)
        if _ext:
            _ext = _ext[1:]
        if _ext in SHORTCUTS:
            name = SHORTCUTS[_ext]

    if options:
        options = dict(map(parse_variable_argument, options))
    else:
        options = dict()

    if not name in REGISTRY:
        raise RuntimeError(
            'Could not resolve {factory_type} factory for {filename} ({name}). Try providing it explicitely using -{opt} <format>.'.
            format(name=name, filename=filename, factory_type=factory_type, opt=factory_type[0])
        )

    if factory_type == READER:
        return REGISTRY[name][0], options
    elif factory_type == WRITER:
        return REGISTRY[name][1], options
    else:
        raise ValueError('Invalid factory type.')


@tuplize
def resolve_filters(filters):
    registry = WorkingDirectoryModulesRegistry()
    for f in filters:
        try:
            mod, attr = f.split(':', 1)
            yield getattr(registry.require(mod), attr)
        except ValueError:
            yield getattr(bonobo, f)


def execute(
    input,
    output,
    reader=None,
    reader_option=None,
    writer=None,
    writer_option=None,
    option=None,
    filter=None,
):
    reader_factory, reader_option = resolve_factory(reader, input, READER, (option or []) + (reader_option or []))

    if output == '-':
        writer_factory, writer_option = bonobo.PrettyPrinter, {}
    else:
        writer_factory, writer_option = resolve_factory(writer, output, WRITER, (option or []) + (writer_option or []))

    filters = resolve_filters(filter)

    graph = bonobo.Graph()
    graph.add_chain(
        reader_factory(input, **reader_option),
        *filters,
        writer_factory(output, **writer_option),
    )

    return bonobo.run(
        graph, services={
            'fs': bonobo.open_fs(),
        }
    )


def register(parser):
    parser.add_argument('input', help='Input filename.')
    parser.add_argument('output', help='Output filename.')
    parser.add_argument(
        '--' + READER,
        '-r',
        help='Choose the reader factory if it cannot be detected from extension, or if detection is wrong.'
    )
    parser.add_argument(
        '--' + WRITER,
        '-w',
        help=
        'Choose the writer factory if it cannot be detected from extension, or if detection is wrong (use - for console pretty print).'
    )
    parser.add_argument(
        '--filter',
        '-f',
        dest='filter',
        action='append',
        help='Add a filter between input and output',
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
    return execute
