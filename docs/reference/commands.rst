Command-line
============


Bonobo Convert
::::::::::::::

Build a simple bonobo graph with one reader and one writer, then execute it, allowing to use bonobo in "no code" mode
for simple file format conversions.

Syntax: `bonobo convert [-r reader] input_filename [-w writer] output_filename`

.. todo::

    add a way to override default options of reader/writers, add a way to add "filters", for example this could be used
    to read from csv and write to csv too (or other format) but adding a geocoder filter that would add some fields.


Bonobo Init
:::::::::::

Create an empty project, ready to use bonobo.

Syntax: `bonobo init`

Requires `cookiecutter`.


Bonobo Inspect
::::::::::::::

Inspects a bonobo file by rendering its transformation graph.
For now, only graphviz output is supported.

Syntax: `bonobo inspect [--graph|-g] [--open|-O] filename`

If the --open option is used, the transformation graph will be opened in the default web browser.
Otherwise the graphviz source code will be printed for the user to use in other tools.


Bonobo Run
::::::::::

Run a transformation graph.

Syntax: `bonobo run [-c cmd | -m mod | file | -] [arg]`

.. todo:: implement -m, check if -c is of any use and if yes, implement it too. Implement args, too.


Bonobo RunC
:::::::::::

Run a transformation graph in a docker container.

Syntax: `bonobo runc [-c cmd | -m mod | file | -] [arg]`

.. todo:: implement -m, check if -c is of any use and if yes, implement it too. Implement args, too.

Requires `bonobo-docker`, install with `docker` extra: `pip install bonobo[docker]`.

