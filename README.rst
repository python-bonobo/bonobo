🐵  bonobo
=========

Data-processing. By monkeys. For humans.

Bonobo is a data-processing library for python 3.5+ that emphasises writing
simple, atomic, plain old python functions and chaining them using a basic
acyclic graph. The nodes will need a bit of plumbery to be runnable in
different means (iteratively, in threads, in processes, on different machines
...) but that should be as transparent as possible.

The only thing asked of the developer is to write "pure" functions to
process data (create a new dict, don't change in place, etc.), and everything
should be fine from this point.

It's a young rewrite of an old python2.7 tool that ran millions of
transformations per day for years on production, so as though it may not yet 
be complete or fully stable (please, allow us to reach 1.0), the underlying
concepts work.

* Documentation: http://docs.bonobo-project.org/
* Release announcements: http://eepurl.com/csHFKL
* Old project (for reference, don't use anymore, instead, help us recode the missing parts in bonobo): http://etl.rdc.li/


.. image:: https://travis-ci.org/python-bonobo/bonobo.svg?branch=0.2
    :target: https://travis-ci.org/python-bonobo/bonobo
    :alt: Continuous Integration

.. image:: https://landscape.io/github/python-bonobo/bonobo/0.2/landscape.svg?style=flat
   :target: https://landscape.io/github/python-bonobo/bonobo/0.2
   :alt: Code Health

.. image:: https://img.shields.io/coveralls/python-bonobo/bonobo.svg
    :target: https://coveralls.io/github/python-bonobo/bonobo?branch=0.2
    :alt: Coverage

.. image:: https://readthedocs.org/projects/bonobo/badge/?version=0.2
    :target: http://docs.bonobo-project.org/
    :alt: Documentation

.. image:: https://img.shields.io/github/downloads/python-bonobo/bonobo/total.svg
    :target: https://github.com/python-bonobo/bonobo/releases
    :alt: Downloads

.. image:: https://img.shields.io/pypi/dm/bonobo.svg
    :target: https://pypi.python.org/pypi/bonobo
    :alt: Python Package on PyPI

----

Issues: https://github.com/python-bonobo/bonobo/issues

Roadmap: https://www.bonobo-project.org/roadmap

Slack: https://bonobo-slack.herokuapp.com/

----

Made with ♥ by `Romain Dorgueil <https://twitter.com/rdorgueil>`_ and `contributors <https://github.com/python-bonobo/bonobo/graphs/contributors>`_.

