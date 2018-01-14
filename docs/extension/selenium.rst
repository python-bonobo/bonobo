Working with Selenium
=====================

.. include:: _alpha.rst

Writing web crawlers with Bonobo and Selenium is easy.

First, install **bonobo-selenium**:

.. code-block:: shell-session

    $ pip install bonobo-selenium

The idea is to have one callable crawl one thing and delegate drill downs to callables further away in the chain.

An example chain could be:

.. graphviz::

    digraph {
        rankdir = LR;
        login -> paginate -> list -> details -> "ExcelWriter(...)";
    }

Where each step would do the following:

* `login()` is in charge to open an authenticated session in the browser.
* `paginate()` open each page of a fictive list and pass it to next.
* `list()` take every list item and yield it.
* `details()` extract the data you're interested in.
* ... and the writer saves it somewhere.

Installation
::::::::::::

Overview
::::::::

Details
:::::::
