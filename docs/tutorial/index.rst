First steps
===========

What is Bonobo?
:::::::::::::::

Bonobo is an ETL (Extract-Transform-Load) framework for python 3.5. The goal is to define data-transformations, with
python code in charge of handling similar shaped independant lines of data.

Bonobo *is not* a statistical or data-science tool. If you're looking for a data-analysis tool in python, use Pandas.

Bonobo is a lean manufacturing assembly line for data that let you focus on the actual work instead of the plumbery.

Tutorial
::::::::

.. toctree::
    :maxdepth: 2

    tut01
    tut02


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

* :doc:`../guide/ext/docker`: run transformation graphs in isolated containers.
* :doc:`../guide/ext/jupyter`: run transformations within jupyter notebooks.
* :doc:`../guide/ext/selenium`: crawl the web using a real browser and work with the gathered data.
* :doc:`../guide/ext/sqlalchemy`: everything you need to interract with SQL databases.

