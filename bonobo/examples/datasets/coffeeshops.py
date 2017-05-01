"""
Extracts a list of parisian bars where you can buy a coffee for a reasonable price, and store them in a flat text file.

.. graphviz::

    digraph {
        rankdir = LR;
        stylesheet = "../_static/graphs.css";

        BEGIN [shape="point"];
        BEGIN -> "ODS()" -> "transform" -> "FileWriter()";
    }

"""

import bonobo
from bonobo.commands.run import get_default_services
from bonobo.ext.opendatasoft import OpenDataSoftAPI

filename = 'coffeeshops.txt'

graph = bonobo.Graph(
    OpenDataSoftAPI(dataset='liste-des-cafes-a-un-euro', netloc='opendata.paris.fr'),
    lambda row: '{nom_du_cafe}, {adresse}, {arrondissement} Paris, France'.format(**row),
    bonobo.FileWriter(path=filename),
)

if __name__ == '__main__':
    bonobo.run(graph, services=get_default_services(__file__))
