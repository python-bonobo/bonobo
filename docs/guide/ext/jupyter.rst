Bonobo with Jupyter
===================

There is a builtin plugin that integrates (kind of minimalistically, for now) bonobo within jupyter notebooks, so
you can read the execution status of a graph within a nice (ok not so nice) html/javascript widget.

See https://github.com/jupyter-widgets/widget-cookiecutter for the base template used.

Installation
::::::::::::

Install `bonobo` with the **jupyter** extra::

    pip install bonobo[jupyter]

Install the jupyter extension::

    jupyter nbextension enable --py --sys-prefix bonobo.ext.jupyter

Development
:::::::::::

To install the widget for development, make sure you're using an editable install of bonobo (see install document)::

    jupyter nbextension install --py --symlink --sys-prefix bonobo.ext.jupyter
    jupyter nbextension enable --py --sys-prefix bonobo.ext.jupyter

If you wanna change the javascript, you should run webpack in watch mode in some terminal::

    cd bonobo/ext/jupyter/js
    npm install
    ./node_modules/.bin/webpack --watch

To compile the widget into a distributable version (which gets packaged on PyPI when a release is made), just run
webpack::

    ./node_modules/.bin/webpack

