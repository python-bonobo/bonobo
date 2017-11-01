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


Bonobo Inspect
::::::::::::::

Inspects a bonobo graph source files. For now, only support graphviz output.

Syntax: `bonobo inspect [--graph|-g] filename`

Requires graphviz if you want to generate an actual graph picture, although the command itself depends on nothing.


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

