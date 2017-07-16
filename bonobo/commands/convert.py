import mimetypes

import bonobo

SHORTCUTS = {
    'plain': 'text/plain',
    'txt': 'text/plain',
    'text': 'text/plain',
    'csv': 'text/csv',
    'json': 'application/json',
}

REGISTRY = {
    'application/json': (bonobo.JsonReader, bonobo.JsonWriter),
    'pickle': (bonobo.PickleReader, bonobo.PickleWriter),
    'text/csv': (bonobo.CsvReader, bonobo.CsvWriter),
    'text/plain': (bonobo.FileReader, bonobo.FileWriter),
}


def resolve_factory(name, filename, factory_type):
    """
    Try to resolve which transformation factory to use for this filename. User eventually provided a name, which has
    priority, otherwise we try to detect it using the mimetype detection on filename.

    """
    if name is None:
        name = mimetypes.guess_type(filename)[0]

    if name in SHORTCUTS:
        name = SHORTCUTS[name]

    if not name in REGISTRY:
        raise RuntimeError('Could not resolve {factory_type} factory for {filename} ({name}). Try providing it explicitely using -{opt} <format>.'.format(name=name, filename=filename, factory_type=factory_type, opt=factory_type[0]))

    if factory_type == 'reader':
        return REGISTRY[name][0]
    elif factory_type == 'writer':
        return REGISTRY[name][1]
    else:
        raise ValueError('Invalid factory type.')

def execute(input, output, reader=None, reader_options=None, writer=None, writer_options=None, options=None):
    reader = resolve_factory(reader, input, 'reader')(input)
    writer = resolve_factory(writer, output, 'writer')(output)

    graph = bonobo.Graph()
    graph.add_chain(reader, writer)

    return bonobo.run(graph, services={
            'fs': bonobo.open_fs(),
        })

def register(parser):
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--reader', '-r')
    parser.add_argument('--writer', '-w')
    # parser.add_argument('--reader-option', '-ro', dest='reader_options')
    # parser.add_argument('--writer-option', '-wo', dest='writer_options')
    # parser.add_argument('--option', '-o', dest='options')
    return execute
