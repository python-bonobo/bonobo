"""
Extracts a list of fablabs in the world, restricted to the ones in france, then format its both for a nice console output
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

import bonobo
from bonobo import examples
from bonobo.contrib.opendatasoft import OpenDataSoftAPI
from bonobo.examples.datasets.services import get_services

try:
    import pycountry
except ImportError as exc:
    raise ImportError('You must install package "pycountry" to run this example.') from exc

API_DATASET = 'fablabs@public-us'
ROWS = 100


def _getlink(x):
    return x.get('url', None)


def normalize(row):
    result = {
        **row,
        'links': list(filter(None, map(_getlink, json.loads(row.get('links'))))),
        'country': pycountry.countries.get(alpha_2=row.get('country_code', '').upper()).name,
    }
    return result


def get_graph(graph=None, *, _limit=(), _print=()):
    graph = graph or bonobo.Graph()
    graph.add_chain(
        OpenDataSoftAPI(dataset=API_DATASET),
        *_limit,
        normalize,
        bonobo.UnpackItems(0),
        *_print,
        bonobo.JsonWriter(path='fablabs.json'),
    )
    return graph


if __name__ == '__main__':
    parser = examples.get_argument_parser()

    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**examples.get_graph_options(options)), services=get_services())
