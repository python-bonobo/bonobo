import io
import re

import requests

import bonobo

EXAMPLES_BASE_URL = 'https://raw.githubusercontent.com/python-bonobo/bonobo/master/bonobo/examples/'
"""The URL to our git repository, in raw mode."""


def _write_response(response, fout):
    """Read the response and write it to the output stream in chunks."""
    for chunk in response.iter_content(io.DEFAULT_BUFFER_SIZE):
        fout.write(chunk)


def _open_url(url):
    """Open a HTTP connection to the URL and return a file-like object."""
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise IOError('unable to download {}, HTTP {}'.format(url, response.status_code))
    return response


def execute(path, *args, **kwargs):
    path = path.lstrip('/')
    if not path.startswith('examples'):
        raise ValueError('download command currently supports examples only')
    examples_path = re.sub('^examples/', '', path)
    output_path = bonobo.get_examples_path(examples_path)
    with _open_url(EXAMPLES_BASE_URL + examples_path) as response, open(output_path, 'wb') as fout:
        _write_response(response, fout)
    print('saved to {}'.format(output_path))


def register(parser):
    parser.add_argument('path', help='The relative path of the thing to download.')
    return execute
