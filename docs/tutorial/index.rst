First steps
===========

Bonobo is an ETL (Extract-Transform-Load) framework for python 3.5. The goal is to define data-transformations, with
python code in charge of handling similar shaped independent lines of data.

Bonobo *is not* a statistical or data-science tool. If you're looking for a data-analysis tool in python, use Pandas.

Bonobo is a lean manufacturing assembly line for data that let you focus on the actual work instead of the plumbery
(execution contexts, parallelism, error handling, console output, logging, ...).

Bonobo uses simple python and should be quick and easy to learn.

**Tutorials**

.. toctree::
    :maxdepth: 1

    1-init
    2-jobs
    3-files
    4-services
    5-packaging

**What's next?**

Once you're familiar with all the base concepts, you can...

* Read the :doc:`Guides </guide/index>` to have a deep dive in each concept.
* Explore the :doc:`Extensions </extension/index>` to widen the possibilities:

  * :doc:`/extension/django`
  * :doc:`/extension/docker`
  * :doc:`/extension/jupyter`
  * :doc:`/extension/sqlalchemy`

* Open the :doc:`References </reference/index>` and start hacking like crazy.

**You're not alone!**

Good documentation is not easy to write.

Although all content here should be accurate, you may feel a lack of completeness, for which we plead guilty and
apologize.

If you're stuck, please come to the `Bonobo Slack Channel <https://bonobo-slack.herokuapp.com/>`_ and we'll figure it
out.

If you're not stuck but had trouble understanding something, please consider contributing to the docs (using GitHub
pull requests).

.. include:: _wip_note.rst
