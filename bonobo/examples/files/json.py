import bonobo

from ._services import get_services

url = 'https://data.toulouse-metropole.fr/explore/dataset/theatres-et-salles-de-spectacles/download?format=json&timezone=Europe/Berlin&use_labels_for_header=true'

graph = bonobo.Graph(
    bonobo.JsonReader(path=url),
    print
)

if __name__ == '__main__':
    bonobo.run(graph)
