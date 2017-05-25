import bonobo
from fs.tarfs import TarFS
import os


def cleanse_sms(row):

    if row['category'] == 'spam':
        row['sms_clean'] = '**MARKED AS SPAM** ' + row['sms'][0:50] + ('...' if len(row['sms']) > 50 else '')
    else:
        row['sms_clean'] = row['sms']

    return row['sms_clean']


graph = bonobo.Graph(
    bonobo.PickleReader('spam.pkl'),        # spam.pkl is within the gzipped tarball
    cleanse_sms,
    print
)


if __name__ == '__main__':

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

    services = {
        'fs': TarFS(
            os.path.join(bonobo.get_examples_path(), 'datasets', 'spam.tgz')
        )
    }
    bonobo.run(graph, services=services)
