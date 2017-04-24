import json
import os

from bonobo import Tee, JsonWriter, Graph, get_examples_path
from bonobo.ext.opendatasoft import OpenDataSoftAPI

from colorama import Fore, Style
try:
    import pycountry
except ImportError as exc:
    raise ImportError('You must install package "pycountry" to run this example.') from exc

API_DATASET = 'fablabs-in-the-world'
API_NETLOC = 'datanova.laposte.fr'
ROWS = 100

__path__ = os.path.dirname(__file__)


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
    print(Style.BRIGHT, row.get('name'), Style.RESET_ALL, sep='')

    address = list(
        filter(
            None, (
                ' '.join(filter(None, (row.get('postal_code', None), row.get('city', None)))), row.get('county', None),
                row.get('country'),
            )
        )
    )

    print('  - {}address{}: {address}'.format(Fore.BLUE, Style.RESET_ALL, address=', '.join(address)))
    print('  - {}links{}: {links}'.format(Fore.BLUE, Style.RESET_ALL, links=', '.join(row['links'])))
    print('  - {}geometry{}: {geometry}'.format(Fore.BLUE, Style.RESET_ALL, **row))
    print('  - {}source{}: {source}'.format(Fore.BLUE, Style.RESET_ALL, source='datanova/' + API_DATASET))


graph = Graph(
    OpenDataSoftAPI(dataset=API_DATASET, netloc=API_NETLOC, timezone='Europe/Paris'),
    normalize,
    filter_france,
    Tee(display),
    JsonWriter(path=get_examples_path('datasets/fablabs.txt')),
)

if __name__ == '__main__':
    from bonobo import run

    run(graph)
