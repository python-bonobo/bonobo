import json

from blessings import Terminal

from bonobo import console_run, tee, JsonWriter
from bonobo.ext.opendatasoft import from_opendatasoft_api

try:
    import pycountry
except ImportError as exc:
    raise ImportError('You must install package "pycountry" to run this example.') from exc

API_DATASET = 'fablabs-in-the-world'
API_NETLOC = 'datanova.laposte.fr'
ROWS = 100

t = Terminal()


def _getlink(x):
    return x.get('url', None)


def normalize(row):
    result = {
        **
        row,
        'links': list(filter(None, map(_getlink, json.loads(row.get('links'))))),
        'country': pycountry.countries.get(alpha_2=row.get('country_code', '').upper()).name,
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
    print('  - {}: {source}'.format(t.blue('source'), source='datanova/' + API_DATASET))


if __name__ == '__main__':
    console_run(
        from_opendatasoft_api(
            API_DATASET, netloc=API_NETLOC, timezone='Europe/Paris'),
        normalize,
        filter_france,
        tee(display),
        JsonWriter('fablabs.json'),
        output=True, )
