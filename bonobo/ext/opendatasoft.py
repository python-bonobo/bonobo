from urllib.parse import urlencode

import requests  # todo: make this a service so we can substitute it ?

from bonobo.config import Configurable, Option
from bonobo.context import ContextProcessor, contextual
from bonobo.util.compat import deprecated
from bonobo.util.objects import ValueHolder


def path_str(path):
    return path if path.startswith('/') else '/' + path


@contextual
class OpenDataSoftAPI(Configurable):
    dataset = Option(str, required=True)
    endpoint = Option(str, default='{scheme}://{netloc}{path}')
    scheme = Option(str, default='https')
    netloc = Option(str, default='data.opendatasoft.com')
    path = Option(path_str, default='/api/records/1.0/search/')
    rows = Option(int, default=500)
    limit = Option(int, default=None)
    timezone = Option(str, default='Europe/Paris')
    kwargs = Option(dict, default=dict)

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
                yield {**row.get('fields', {}), 'geometry': row.get('geometry', {})}

            start.value += self.rows


@deprecated
def from_opendatasoft_api(dataset, **kwargs):
    return OpenDataSoftAPI(dataset=dataset, **kwargs)


__all__ = [
    'OpenDataSoftAPI',
]
