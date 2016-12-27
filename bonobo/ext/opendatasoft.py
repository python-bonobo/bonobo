from urllib.parse import urlencode

import requests  # todo: make this a service so we can substitute it ?


def from_opendatasoft_api(dataset=None,
                          endpoint='{scheme}://{netloc}{path}',
                          scheme='https',
                          netloc='data.opendatasoft.com',
                          path='/api/records/1.0/search/',
                          rows=100,
                          **kwargs):
    path = path if path.startswith('/') else '/' + path
    params = (
        ('dataset', dataset),
        ('rows', rows), ) + tuple(sorted(kwargs.items()))
    base_url = endpoint.format(scheme=scheme, netloc=netloc, path=path) + '?' + urlencode(params)

    def _extract_ods():
        nonlocal base_url, rows
        start = 0
        while True:
            resp = requests.get('{}&start={start}'.format(base_url, start=start))
            records = resp.json().get('records', [])

            if not len(records):
                break

            for row in records:
                yield { ** row.get('fields', {}), 'geometry': row.get('geometry', {})}

            start += rows

    _extract_ods.__name__ = 'extract_' + dataset.replace('-', '_')
    return _extract_ods
