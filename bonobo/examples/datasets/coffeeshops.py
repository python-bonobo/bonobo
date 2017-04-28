import bonobo
from bonobo.ext.opendatasoft import OpenDataSoftAPI

filename = 'coffeeshops.txt'

graph = bonobo.Graph(
    OpenDataSoftAPI(dataset='liste-des-cafes-a-un-euro', netloc='opendata.paris.fr'),
    lambda row: '{nom_du_cafe}, {adresse}, {arrondissement} Paris, France'.format(**row),
    bonobo.FileWriter(path=filename),
)


def get_services():
    from os.path import dirname
    return {
        'fs': bonobo.open_fs(dirname(__file__))
    }


if __name__ == '__main__':
    bonobo.run(graph, services=get_services())
