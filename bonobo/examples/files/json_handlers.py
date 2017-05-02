import bonobo
from bonobo.commands.run import get_default_services


def get_fields(row):
    return row['fields']


graph = bonobo.Graph(
    bonobo.JsonReader('datasets/theaters.json'),
    get_fields,
    bonobo.PrettyPrint(title_keys=('eq_nom_equipement', )),
)

if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__))
