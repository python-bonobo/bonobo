from os.path import dirname, realpath, join

import bonobo
from bonobo.ext.opendatasoft import OpenDataSoftAPI

OUTPUT_FILENAME = realpath(join(dirname(__file__), 'coffeeshops.txt'))

graph = bonobo.Graph(
    OpenDataSoftAPI(dataset='liste-des-cafes-a-un-euro', netloc='opendata.paris.fr'),
    lambda row: '{nom_du_cafe}, {adresse}, {arrondissement} Paris, France'.format(**row),
    bonobo.FileWriter(path=OUTPUT_FILENAME),
)

if __name__ == '__main__':
    bonobo.run(graph)
    print('Import done, read {} for results.'.format(OUTPUT_FILENAME))
