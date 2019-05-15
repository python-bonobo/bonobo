Working with Jupyter
====================

.. include:: _beta.rst

There is a builtin plugin that integrates (somewhat minimallistically, for now) bonobo within jupyter notebooks, so
you can read the execution status of a graph within a nice (ok, not so nice) html/javascript widget.

Installation
::::::::::::

Install `bonobo` with the **jupyter** extra::

    pip install bonobo[jupyter]

Install the jupyter extension::

    jupyter nbextension enable --py --sys-prefix widgetsnbextension
    jupyter nbextension enable --py --sys-prefix bonobo.contrib.jupyter

Development
:::::::::::

You should favor yarn over npm to install node packages. If you prefer to use npm, it's up to you to adapt the code.

To install the widget for development, make sure you're using an editable install of bonobo (see install document)::

    jupyter nbextension install --py --symlink --sys-prefix bonobo.contrib.jupyter
    jupyter nbextension enable --py --sys-prefix bonobo.contrib.jupyter

If you want to change the javascript, you should run webpack in watch mode in some terminal::

    cd bonobo/ext/jupyter/js
    yarn install
    ./node_modules/.bin/webpack --watch

To compile the widget into a distributable version (which gets packaged on PyPI when a release is made), just run
webpack::

    ./node_modules/.bin/webpack


Source code
:::::::::::

https://github.com/python-bonobo/bonobo/tree/master/bonobo/contrib/jupyter
