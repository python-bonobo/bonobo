import os

import bonobo
from bonobo import examples
from bonobo.examples.datasets.coffeeshops import get_graph as get_coffeeshops_graph
from bonobo.examples.datasets.fablabs import get_graph as get_fablabs_graph
from bonobo.examples.datasets.services import get_datasets_dir, get_minor_version, get_services

graph_factories = {'coffeeshops': get_coffeeshops_graph, 'fablabs': get_fablabs_graph}

if __name__ == '__main__':
    parser = examples.get_argument_parser()
    parser.add_argument('--target', '-t', choices=graph_factories.keys(), nargs='+')
    parser.add_argument('--sync', action='store_true', default=False)

    with bonobo.parse_args(parser) as options:
        graph_options = examples.get_graph_options(options)
        graph_names = list(options['target'] if options['target'] else sorted(graph_factories.keys()))

        # Create a graph with all requested subgraphs
        graph = bonobo.Graph()
        for name in graph_names:
            graph = graph_factories[name](graph, **graph_options)

        bonobo.run(graph, services=get_services())

        if options['sync']:
            # TODO: when parallel option for node will be implemented, need to be rewriten to use a graph.
            import boto3

            s3 = boto3.client('s3')

            local_dir = get_datasets_dir()
            for root, dirs, files in os.walk(local_dir):
                for filename in files:
                    local_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(local_path, local_dir)
                    s3_path = os.path.join(get_minor_version(), relative_path)

                    try:
                        s3.head_object(Bucket='bonobo-examples', Key=s3_path)
                    except:
                        s3.upload_file(local_path, 'bonobo-examples', s3_path, ExtraArgs={'ACL': 'public-read'})
