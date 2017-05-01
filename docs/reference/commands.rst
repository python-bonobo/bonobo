Command-line
============

Bonobo Init
:::::::::::

Create an empty project, ready to use bonobo.

Syntax: `bonobo init`

Requires `edgy.project`.


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

