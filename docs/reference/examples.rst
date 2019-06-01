Examples
========

There are a few examples bundled with **bonobo**.

You'll find them under the :mod:`bonobo.examples` package, and you can run them directly as modules:

.. code-block:: shell-session

    $ bonobo run -m bonobo.examples.module


or

.. code-block:: shell-session

    $ python -m bonobo.examples.module



.. toctree::
    :maxdepth: 4

    examples/tutorials


Datasets
::::::::


.. module:: bonobo.examples.datasets

The :mod:`bonobo.examples.datasets` package contains examples that generates datasets locally for other examples to
use. As of today, we commit the content of those datasets to git, even if that may be a bad idea, so all the examples
are easily runnable. Later, we'll see if we favor a "missing dependency exception" approach.


Coffeeshops
-----------

.. automodule:: bonobo.examples.datasets.coffeeshops
    :members:
    :undoc-members:
    :show-inheritance:

Fablabs
-------

.. automodule:: bonobo.examples.datasets.fablabs
    :members:
    :undoc-members:
    :show-inheritance:

Types
:::::

Strings
-------

.. automodule:: bonobo.examples.types.strings
    :members: graph, extract, transform, load
    :undoc-members:
    :show-inheritance:


Dicts
-----

.. automodule:: bonobo.examples.types.dicts
    :members: graph, extract, transform, load
    :undoc-members:
    :show-inheritance:


Bags
----

.. automodule:: bonobo.examples.types.bags
    :members: graph, extract, transform, load
    :undoc-members:
    :show-inheritance:


Utils
:::::

Count
-----

.. automodule:: bonobo.examples.nodes.count
    :members:
    :undoc-members:
    :show-inheritance:


