from urllib.parse import urlencode

import requests  # todo: make this a service so we can substitute it ?


def extract_ods(url, dataset, rows=100, **kwargs):
    params = (
        ('dataset', dataset),
        ('rows', rows), ) + tuple(sorted(kwargs.items()))
    base_url = url + '?' + urlencode(params)

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
