Detailed roadmap
================

Next...
:::::::

* Release process specialised for bonobo. With changelog production, etc.
* Document how to upgrade version, like, minor need change badges, etc.
* PyPI page looks like crap: https://pypi.python.org/pypi/bonobo/0.2.1
* Windows break because of readme encoding. Fix in edgy.
* bonobo init --with sqlalchemy,docker
* logger, vebosity level
* Console run should allow console plugin as a command line argument (or silence it).
* ContextProcessors not clean

Version 0.3
:::::::::::

* Services !
* SQLAlchemy 101

Version 0.2
:::::::::::

* Autodetect if within jupyter notebook context, and apply plugin if it's the case.
* New bonobo.structs package with simple data structures (bags, graphs, tokens).

Plugins API
:::::::::::

* Stabilize, find other things to do.

Minor stuff
:::::::::::

* Should we include datasets in the repo or not? As they may change, grow, and even eventually have licenses we can't use,
  it's probably best if we don't.