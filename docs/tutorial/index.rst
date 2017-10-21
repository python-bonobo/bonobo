First steps
===========

What is Bonobo?
:::::::::::::::

Bonobo is an ETL (Extract-Transform-Load) framework for python 3.5. The goal is to define data-transformations, with
python code in charge of handling similar shaped independent lines of data.

Bonobo *is not* a statistical or data-science tool. If you're looking for a data-analysis tool in python, use Pandas.

Bonobo is a lean manufacturing assembly line for data that let you focus on the actual work instead of the plumbery
(execution contexts, parallelism, error handling, console output, logging, ...).

Bonobo uses simple python and should be quick and easy to learn.

Tutorial
::::::::

.. note::

    Good documentation is not easy to write. We do our best to make it better and better.

    Although all content here should be accurate, you may feel a lack of completeness, for which we plead guilty and
    apologize.

    If you're stuck, please come and ask on our `slack channel <https://bonobo-slack.herokuapp.com/>`_, we'll figure
    something out.

    If you're not stuck but had trouble understanding something, please consider contributing to the docs (via GitHub
    pull requests).

.. toctree::
    :maxdepth: 2

    tut01
    tut02
    tut03
    tut04


What's next?
::::::::::::

Read a few examples
-------------------

* :doc:`../reference/examples`

Read about best development practices
-------------------------------------

* :doc:`../guide/index`
* :doc:`../guide/purity`

Read about integrating external tools with bonobo
-------------------------------------------------

* :doc:`../extension/docker`: run transformation graphs in isolated containers.
* :doc:`../extension/jupyter`: run transformations within jupyter notebooks.
* :doc:`../extension/selenium`: crawl the web using a real browser and work with the gathered data.
* :doc:`../extension/sqlalchemy`: everything you need to interract with SQL databases.

