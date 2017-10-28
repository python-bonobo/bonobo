import io
import re
import urllib.request

import bonobo

EXAMPLES_BASE_URL = 'https://raw.githubusercontent.com/python-bonobo/bonobo/master/bonobo/examples/'
"""The URL to our git repository, in raw mode."""


def _save_stream(fin, fout):
    """Read the input stream and write it to the output stream block-by-block."""
    while True:
        data = fin.read(io.DEFAULT_BUFFER_SIZE)
        if data:
            fout.write(data)
        else:
            break


def _open_url(url):
    """Open a HTTP connection to the URL and return a file-like object."""
    response = urllib.request.urlopen(url)
    if response.getcode() != 200:
        raise IOError('unable to download {}, HTTP {}'.format(url, response.getcode()))
    return response


def execute(path, *args, **kwargs):
    path = path.lstrip('/')
    if not path.startswith('examples'):
        raise ValueError('download command currently supports examples only')
    examples_path = re.sub('^examples/', '', path)
    output_path = bonobo.get_examples_path(examples_path)
    fin = _open_url(EXAMPLES_BASE_URL + examples_path)
    with open(output_path, 'wb') as fout:
        _save_stream(fin, fout)
    print('saved to {}'.format(output_path))


def register(parser):
    parser.add_argument('path', help='The relative path of the thing to download.')
    return execute
