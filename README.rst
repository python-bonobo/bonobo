==========
🐵  bonobo
==========

Data-processing. By monkeys. For humans.

.. image:: https://img.shields.io/pypi/v/bonobo.svg
    :target: https://pypi.python.org/pypi/bonobo
    :alt: PyPI

.. image:: https://img.shields.io/pypi/wheel/bonobo.svg
    :target: https://pypi.python.org/pypi/bonobo
    :alt: Wheel

.. image:: https://img.shields.io/pypi/pyversions/bonobo.svg
    :target: https://pypi.python.org/pypi/bonobo
    :alt: Versions

.. image:: https://readthedocs.org/projects/bonobo/badge/?version=0.2
    :target: http://docs.bonobo-project.org/
    :alt: Documentation

.. image:: https://travis-ci.org/python-bonobo/bonobo.svg?branch=0.2
    :target: https://travis-ci.org/python-bonobo/bonobo
    :alt: Continuous Integration

.. image:: https://api.codacy.com/project/badge/Grade/60aa1ba3ee7b4b4ebd71ca659736c0af
   :target: https://www.codacy.com/app/hartym/bonobo
   :alt: Code Health from codacy

.. image:: https://landscape.io/github/python-bonobo/bonobo/0.2/landscape.svg?style=flat
   :target: https://landscape.io/github/python-bonobo/bonobo/0.2
   :alt: Code Health from landscape

.. image:: https://img.shields.io/coveralls/python-bonobo/bonobo.svg
    :target: https://coveralls.io/github/python-bonobo/bonobo?branch=0.2
    :alt: Coverage

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

----

*Bonobo is under heavy development, we're making the best efforts to keep the core as stable as possible but we also need to move forward. Please allow us to reach 1.0 stability and our sincere apologies for anything we'd break in the process (feel free to complain on issues, so we notice breakages we did not expect)*

----

Documentation: http://docs.bonobo-project.org/

Issues: https://github.com/python-bonobo/bonobo/issues

Roadmap: https://www.bonobo-project.org/roadmap

Slack: https://bonobo-slack.herokuapp.com/

Release announcements: http://eepurl.com/csHFKL

----

Made with ♥ by `Romain Dorgueil <https://twitter.com/rdorgueil>`_ and `contributors <https://github.com/python-bonobo/bonobo/graphs/contributors>`_.
    
.. image:: https://img.shields.io/pypi/l/bonobo.svg
    :target: https://pypi.python.org/pypi/bonobo
    :alt: License


