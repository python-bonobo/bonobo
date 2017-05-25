Internal roadmap notes
======================

Things that should be thought about and/or implemented, but that I don't know where to store.

Graph and node level plugins
::::::::::::::::::::::::::::

 * Enhancers or node-level plugins
 * Graph level plugins
 * Documentation

Command line interface and environment
::::::::::::::::::::::::::::::::::::::

* How do we manage environment ? .env ?
* How do we configure plugins ?

Services and Processors
:::::::::::::::::::::::

* ContextProcessors not clean (a bit better, but still not in love with the api)

Next...
:::::::

* Release process specialised for bonobo. With changelog production, etc.
* Document how to upgrade version, like, minor need change badges, etc.
* Windows console looks crappy.
* bonobo init --with sqlalchemy,docker; cookiecutter?
* logger, vebosity level


External libs that looks good
:::::::::::::::::::::::::::::

* dask.distributed
* mediator (event dispatcher)

Version 0.4
:::::::::::

* SQLAlchemy 101

Design decisions
::::::::::::::::

* initialize / finalize better than start / stop ?

Minor stuff
:::::::::::

* Should we include datasets in the repo or not? As they may change, grow, and even eventually have licenses we can't use,
  it's probably best if we don't.