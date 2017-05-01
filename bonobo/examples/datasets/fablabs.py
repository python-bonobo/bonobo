"""
Extracts a list of fablabs in the world, restrict to the ones in france, then format it both for a nice console output
and a flat txt file.

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "ODS()" -> "normalize" -> "filter_france" -> "Tee()" -> "JsonWriter()";
    }

"""

import json

from colorama import Fore, Style

import bonobo
from bonobo.commands.run import get_default_services
from bonobo.ext.opendatasoft import OpenDataSoftAPI

try:
    import pycountry
except ImportError as exc:
    raise ImportError(
        'You must install package "pycountry" to run this example.'
    ) from exc

API_DATASET = 'fablabs-in-the-world'
API_NETLOC = 'datanova.laposte.fr'
ROWS = 100


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
                ' '.join(
                    filter(
                        None, (
                            row.get('postal_code', None),
                            row.get('city', None)
                        )
                    )
                ), row.get('county', None), row.get('country'),
            )
        )
    )

    print(
        '  - {}address{}: {address}'.
        format(Fore.BLUE, Style.RESET_ALL, address=', '.join(address))
    )
    print(
        '  - {}links{}: {links}'.
        format(Fore.BLUE, Style.RESET_ALL, links=', '.join(row['links']))
    )
    print(
        '  - {}geometry{}: {geometry}'.
        format(Fore.BLUE, Style.RESET_ALL, **row)
    )
    print(
        '  - {}source{}: {source}'.format(
            Fore.BLUE, Style.RESET_ALL, source='datanova/' + API_DATASET
        )
    )


graph = bonobo.Graph(
    OpenDataSoftAPI(
        dataset=API_DATASET, netloc=API_NETLOC, timezone='Europe/Paris'
    ),
    normalize,
    filter_france,
    bonobo.Tee(display),
    bonobo.JsonWriter(path='fablabs.txt'),
)

if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__))
