import bonobo
from bonobo.commands.run import get_default_services

# XXX does not work anymore because of filesystem service, can't read HTTP
url = 'https://data.toulouse-metropole.fr/explore/dataset/theatres-et-salles-de-spectacles/download?format=json&timezone=Europe/Berlin&use_labels_for_header=true'

graph = bonobo.Graph(bonobo.JsonReader(path=url), print)

if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__))
