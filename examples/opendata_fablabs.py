import json

from blessings import Terminal
from pycountry import countries

from bonobo.ext.console import console_run
from bonobo.ext.ods import extract_ods
from bonobo.util import tee
from bonobo.io.json import to_json

DATASET = 'fablabs-in-the-world'
SEARCH_URL = 'https://datanova.laposte.fr/api/records/1.0/search/'
URL = SEARCH_URL + '?dataset=' + DATASET
ROWS = 100

t = Terminal()


def _getlink(x):
    return x.get('url', None)


def normalize(row):
    result = {
        **
        row,
        'links': list(filter(None, map(_getlink, json.loads(row.get('links'))))),
        'country': countries.get(alpha_2=row.get('country_code', '').upper()).name,
    }
    return result


def filter_france(row):
    if row.get('country') == 'France':
        yield row


def display(row):
    print(t.bold(row.get('name')))

    address = list(
        filter(None, (
            ' '.join(filter(None, (row.get('postal_code', None), row.get('city', None)))),
            row.get('county', None),
            row.get('country'), )))

    print('  - {}: {address}'.format(t.blue('address'), address=', '.join(address)))
    print('  - {}: {links}'.format(t.blue('links'), links=', '.join(row['links'])))
    print('  - {}: {geometry}'.format(t.blue('geometry'), **row))
    print('  - {}: {source}'.format(t.blue('source'), source='datanova/' + DATASET))


if __name__ == '__main__':
    console_run(
        extract_ods(
            SEARCH_URL, DATASET, timezone='Europe/Paris'),
        normalize,
        filter_france,
        tee(display),
        to_json('fablabs.json'),
        output=True, )
