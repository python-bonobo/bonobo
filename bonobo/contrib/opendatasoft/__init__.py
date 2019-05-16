from urllib.parse import urlencode

import requests  # todo: make this a service so we can substitute it ?

from bonobo.config import Option
from bonobo.config.configurables import Configurable
from bonobo.config.processors import ContextProcessor
from bonobo.util.objects import ValueHolder


def path_str(path):
    return path if path.startswith('/') else '/' + path


class OpenDataSoftAPI(Configurable):
    dataset = Option(str, positional=True)
    endpoint = Option(str, required=False, default='{scheme}://{netloc}{path}')
    scheme = Option(str, required=False, default='https')
    netloc = Option(str, required=False, default='data.opendatasoft.com')
    path = Option(path_str, required=False, default='/api/records/1.0/search/')
    rows = Option(int, required=False, default=500)
    limit = Option(int, required=False)
    timezone = Option(str, required=False, default='Europe/Paris')
    kwargs = Option(dict, required=False, default=dict)

    @ContextProcessor
    def compute_path(self, context):
        params = (('dataset', self.dataset), ('timezone', self.timezone)) + tuple(sorted(self.kwargs.items()))
        yield self.endpoint.format(scheme=self.scheme, netloc=self.netloc, path=self.path) + '?' + urlencode(params)

    @ContextProcessor
    def start(self, context, base_url):
        yield ValueHolder(0)

    def __call__(self, base_url, start, *args, **kwargs):
        while (not self.limit) or (self.limit > start):
            url = '{}&start={start}&rows={rows}'.format(
                base_url, start=start.value, rows=self.rows if not self.limit else min(self.rows, self.limit - start)
            )
            resp = requests.get(url)
            records = resp.json().get('records', [])

            if not len(records):
                break

            for row in records:
                yield {**row.get('fields', {}), 'geometry': row.get('geometry', {}), 'recordid': row.get('recordid')}

            start += self.rows


__all__ = ['OpenDataSoftAPI']
