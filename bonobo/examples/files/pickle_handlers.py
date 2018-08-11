'''
This example shows how a different file system service can be injected
into a transformation (as compressing pickled objects often makes sense
anyways).  The pickle itself contains a list of lists as follows:

```
[
    ['category', 'sms'],
    ['ham', 'Go until jurong point, crazy..'],
    ['ham', 'Ok lar... Joking wif u oni...'],
    ['spam', 'Free entry in 2 a wkly comp to win...'],
    ['ham', 'U dun say so early hor... U c already then say...'],
    ['ham', 'Nah I don't think he goes to usf, he lives around here though'],
    ['spam', 'FreeMsg Hey there darling it's been 3 week's now...'],
    ...
]
```

where the first column categorizes and sms as "ham" or "spam".  The second
column contains the sms itself.

Data set taken from:
https://www.kaggle.com/uciml/sms-spam-collection-dataset/downloads/sms-spam-collection-dataset.zip

The transformation (1) reads the pickled data, (2) marks and shortens
messages categorized as spam, and (3) prints the output.

'''

from fs.tarfs import TarFS

import bonobo
from bonobo import examples


def cleanse_sms(category, sms):
    if category == 'spam':
        sms_clean = '**MARKED AS SPAM** ' + sms[0:50] + ('...' if len(sms) > 50 else '')
    elif category == 'ham':
        sms_clean = sms
    else:
        raise ValueError('Unknown category {!r}.'.format(category))

    return category, sms, sms_clean


def get_graph(*, _limit=(), _print=()):
    graph = bonobo.Graph()

    graph.add_chain(
        # spam.pkl is within the gzipped tarball
        bonobo.PickleReader('spam.pkl'),
        *_limit,
        cleanse_sms,
        *_print,
    )

    return graph


def get_services():
    from ._services import get_services

    return {**get_services(), 'fs': TarFS(bonobo.get_examples_path('datasets/spam.tgz'))}


if __name__ == '__main__':
    parser = examples.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**examples.get_graph_options(options)), services=get_services())
