import io
import re

import requests

import bonobo
from bonobo.commands import BaseCommand

EXAMPLES_BASE_URL = 'https://raw.githubusercontent.com/python-bonobo/bonobo/master/bonobo/examples/'
"""The URL to our git repository, in raw mode."""


class DownloadCommand(BaseCommand):
    def handle(self, *, path, **options):
        if not path.startswith('examples'):
            raise ValueError('Download command currently supports examples only')
        examples_path = re.sub('^examples/', '', path)
        output_path = bonobo.get_examples_path(examples_path)
        with _open_url(EXAMPLES_BASE_URL + examples_path) as response, open(output_path, 'wb') as fout:
            for chunk in response.iter_content(io.DEFAULT_BUFFER_SIZE):
                fout.write(chunk)
        self.logger.info('Download saved to {}'.format(output_path))

    def add_arguments(self, parser):
        parser.add_argument('path', help='The relative path of the thing to download.')


def _open_url(url):
    """Open a HTTP connection to the URL and return a file-like object."""
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise IOError('Unable to download {}, HTTP {}'.format(url, response.status_code))
    return response
