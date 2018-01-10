Part 2: Writing ETL Jobs
========================

In |bonobo|, an ETL job is a graph with some logic to execute it, like the file we created in the previous section.

You can learn more about the :class:`bonobo.Graph` data-structure and its properties in the
:doc:`graphs guide </guide/graphs>`.


Scenario
::::::::

Let's create a sample application, which goal will be to integrate some data in various systems.

We'll use an open-data dataset, containing all the fablabs in the world.

We will normalize this data using a few different rules, then write it somewhere.

In this step, we'll focus on getting this data normalized and output to the console. In the next steps, we'll extend it
to other targets, like files, and databases.


Setup
:::::

We'll change the `tutorial.py` file created in the last step to handle this new scenario.

First, let's remove all boilerplate code, so it looks like this:

.. code-block:: python

    import bonobo


    def get_graph(**options):
        graph = bonobo.Graph()
        return graph


    def get_services(**options):
        return {}


    if __name__ == '__main__':
        parser = bonobo.get_argument_parser()
        with bonobo.parse_args(parser) as options:
            bonobo.run(get_graph(**options), services=get_services(**options))


Your job now contains the logic for executing an empty graph, and we'll complete this with our application logic.

Reading the source data
:::::::::::::::::::::::

Let's add a simple chain to our `get_graph(...)` function, so that it reads from the fablabs open-data api.

The source dataset we'll use can be found on `this site <https://public-us.opendatasoft.com/explore/dataset/fablabs/>`_.
It's licensed under `Public Domain`, which makes it just perfect for our example.

.. note::

    There is a :mod:`bonobo.contrib.opendatasoft` module that makes reading from OpenDataSoft APIs easier, including
    pagination and limits, but for our tutorial, we'll avoid that and build it manually.

Let's write our extractor:

.. code-block:: python

    import requests

    FABLABS_API_URL = 'https://public-us.opendatasoft.com/api/records/1.0/search/?dataset=fablabs&rows=1000'

    def extract_fablabs():
        yield from requests.get(FABLABS_API_URL).json().get('records')

This extractor will get called once, query the API url, parse it as JSON, and yield the items from the "records" list,
one by one.

.. note::

    You'll probably want to make it a bit more verbose in a real application, to handle all kind of errors that can
    happen here. What if the server is down? What if it returns a response which is not JSON? What if the data is not
    in the expected format?

    For simplicity sake, we'll ignore that here but that's the kind of questions you should have in mind when writing
    pipelines.

To test our pipeline, let's use a :class:`bonobo.Limit` and a :class:`bonobo.PrettyPrinter`, and change our
`get_graph(...)` function accordingly:

.. code-block:: python

    import bonobo

    def get_graph(**options):
        graph = bonobo.Graph()
        graph.add_chain(
            extract_fablabs,
            bonobo.Limit(10),
            bonobo.PrettyPrinter(),
        )
        return graph

Running this job should output a bit of data, along with some statistics.

First, let's look at the statistics:

.. code-block:: shell-session

    - extract_fablabs in=1 out=995 [done]
    - Limit in=995 out=10 [done]
    - PrettyPrinter in=10 out=10 [done]

It is important to understand that we extracted everything (995 rows), before droping 99% of the dataset.

This is OK for debugging, but not efficient.

.. note::

    You should always try to limit the amount of data as early as possible, which often means not generating the data
    you won't need in the first place. Here, we could have used the `rows=` query parameter in the API URL to not
    request the data we would anyway drop.

Normalize
:::::::::

.. include:: _todo.rst

Output
::::::

We used :class:`bonobo.PrettyPrinter` to output the data.

It's a flexible transformation provided that helps you display the content of a stream, and you'll probably use it a
lot for various reasons.


Moving forward
::::::::::::::

You now know:

* How to use a reader node.
* How to use the console output.
* How to limit the number of elements in a stream.
* How to pass data from one node to another.
* How to structure a graph using chains.

It's now time to jump to :doc:`3-files`.
