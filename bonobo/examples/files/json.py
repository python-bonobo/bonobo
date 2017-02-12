import bonobo as bb

url = 'https://data.toulouse-metropole.fr/explore/dataset/theatres-et-salles-de-spectacles/download?format=json&timezone=Europe/Berlin&use_labels_for_header=true'

graph = bb.Graph(bb.JsonReader(path=url), print)

if __name__ == '__main__':
    bb.run(graph)
