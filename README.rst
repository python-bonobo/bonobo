🐵  bonobo
=========

Data-processing. By monkeys. For humans.

Bonobo is a data-processing library for python 3.5+ that emphasis writing
simple, atomic, plain old python functions and chaining them using a basic
acyclic graph. The nodes will need a bit of plumbery to be runnable in
different means (iteratively, in threads, in processes, on different machines
...) but that should be as transparent as possible.

The only thing asked to the developer is to either write "pure" functions to
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

Made with ♥ by `Romain Dorgueil <https://twitter.com/rdorgueil>`_ and `contributors <https://github.com/python-bonobo/bonobo/graphs/contributors>`_.

----

Roadmap (in progress)
:::::::::::::::::::::

Bonobo is young. This roadmap is alive, and will evolve. Its only purpose is to
write down incoming things somewhere.

Version 0.2
-----------

* Changelog
* Migration guide
* Update documentation
* Threaded does not terminate anymore
* More tests

Bugs:

- KeyboardInterrupt does not work anymore.
- ThreadPool does not stop anymore.

Configuration
.............

* Support for position arguments (options), required options are good candidates.

Context processors
..................

* Be careful with order, especially with python 3.5. (done)
* @contextual decorator is not clean enough. Once the behavior is right, find a
  way to use regular inheritance, without meta.
* ValueHolder API not clean. Find a better way.

Random thoughts and things to do
................................

* Class-tree for Graph and Nodes

* Class-tree for execution contexts:

  * GraphExecutionContext
  * NodeExecutionContext
  * PluginExecutionContext

* Class-tree for ExecutionStrategies

  * NaiveStrategy
  * PoolExecutionStrategy
    * ThreadPoolExecutionStrategy
    * ProcesPoolExecutionStrategy
  * ThreadExecutionStrategy
  * ProcessExecutionStrategy

* Class-tree for bags

  * Bag
  * ErrorBag
  * InheritingBag

* Co-routines: for unordered, or even ordered but long io.

* "context processors": replace initialize/finalize by a generator that yields only once


* "execute" function:

    .. code-block:: python

        def execute(graph: Graph, *, strategy: ExecutionStrategy, plugins: List[Plugin]) -> Execution:
            pass

* Handling console. Can we use a queue, and replace stdout / stderr ?




