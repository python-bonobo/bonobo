Problems
========

Failed to display Jupyter Widget of type BonoboWidget.
If you're reading this message in Jupyter Notebook or JupyterLab, it may mean that the widgets JavaScript is still loading. If this message persists, it likely means that the widgets JavaScript library is either not installed or not enabled. See the Jupyter Widgets Documentation for setup instructions.
If you're reading this message in another notebook frontend (for example, a static rendering on GitHub or NBViewer), it may mean that your frontend doesn't currently support widgets.

.. code-block:: shell-session

    $ jupyter nbextension enable --py widgetsnbextension
    $ jupyter nbextension install --py --symlink bonobo.contrib.jupyter
    $ jupyter nbextension enable --py bonobo.contrib.jupyter


Todo
====

* Pretty printer


Options for Bags
================

tuple only

pros : simple
cons :
- how to name columns / store headers ?
- how to return a dictionary



yield keys('foo', 'bar', 'baz')


yield 'a', 'b', 'c'


CHANGELOG
=========

* Bags changed to something way closer to namedtuples.
  * Better at managing memory
  * Less flexible for kwargs usage, but much more standard and portable from one to another version of python
  * More future proof for different execution strategies
  * May lead to changes in your current transformation

* A given transformation now have an input and a output "type" which is either manually set by the user or
  detected from the first item sent through a queue. It is a restiction on how bonobo can be used, but
  will help having better predicatability.

* No more "graph" instance detection. This was misleading for new users, and not really pythonic. The
  recommended way to start with bonobo is just to use one python file with a __main__ block, and if the
  project grows, include this file in a package, either new or existing one. The init cli changed to
  help you generate files or packages. That also means that we do not generate things with cookiecutter
  anymore.

* Jupyter enhancements

* Graphviz support

* New nodes in stdlib

* Registry, used for conversions but also for your own integrations.


