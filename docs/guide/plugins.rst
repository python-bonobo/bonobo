Plugins
=======


Graph level plugins
:::::::::::::::::::

Slack
-----

.. code-block:: python

    with bonobo.parse_args(parser) as options:
        context = bonobo.run(get_graph(**options), services={}, plugins=[
            SlackPlugin(
                slack_api_token=os.environ['SLACK_API_TOKEN'],
                env=os.environ['ENV'],
                channel=os.environ['SLACK_CHANNEL'],
                name='My ETL Job',
                report_only_failure=False
            )
        ])

Node level plugins
::::::::::::::::::

enhancers


node
    -


.. include:: _next.rst
