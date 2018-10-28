Installation
============

Create an ETL project
:::::::::::::::::::::

First, install the framework:

.. code-block:: shell-session

    $ pip install --upgrade bonobo

Create a simple job:

.. code-block:: shell-session

    $ bonobo init my-etl.py

And let's go for a test drive:

.. code-block:: shell-session

    $ python my-etl.py

Congratulations, you ran your first Bonobo ETL job.

Now, you can head to :doc:`tutorial/index`.

.. note::

    It's often best to start with a single file then move it into a project
    (which, in python, needs to live in a package).

    You can read more about this topic in the :doc:`guide/packaging` section,
    along with pointers on how to move this first file into an existing fully
    featured python package.


Other installation options
::::::::::::::::::::::::::

Install from PyPI
-----------------

You can install it directly from the `Python Package Index <https://pypi.python.org/pypi/bonobo>`_ (like we did above).

.. code-block:: shell-session

    $ pip install bonobo

To upgrade an existing installation, use `--upgrade`:

.. code-block:: shell-session

    $ pip install --upgrade bonobo


Install from source
-------------------

If you want to install an unreleased version, you can use git urls with pip. This is useful when using bonobo as a
dependency of your code and you want to try a forked version of bonobo with your software. You can use a `git+http`
string in your `requirements.txt` file. However, the best option for development on bonobo is an editable install (see
below).

.. code-block:: shell-session

    $ pip install git+https://github.com/python-bonobo/bonobo.git@develop#egg=bonobo

.. note::

    Here, we use the `develop` branch, which is the incoming unreleased minor version. It's the way to "live on the
    edge", either to test your codebase with a future release, or to test unreleased features. You can use this
    technique to install any branch you want, and even a branch in your own repository.


Editable install
----------------

If you plan on making patches to Bonobo, you should install it as an "editable" package, which is a really great pip
feature. Pip will clone your repository in a source directory and create a symlink for it in the site-package directory
of your python interpreter.

.. code-block:: shell-session

    $ pip install --editable git+https://github.com/python-bonobo/bonobo.git@develop#egg=bonobo

.. note:: You can also use `-e`, the shorthand version of `--editable`.

.. note:: Once again, we use `develop` here. New features should go to `develop`, while bugfixes can go to `master`.

If you can't find the "source" directory, try running this:

.. code-block:: shell-session

    $ python -c "import bonobo; print(bonobo.__path__)"

Local clone
-----------

Another option is to have a "local" editable install, which means you create the clone by yourself and make an editable install
from the local clone.

.. code-block:: shell-session

    $ git clone git@github.com:python-bonobo/bonobo.git
    $ cd bonobo
    $ pip install --editable .

You can develop on this clone, but you probably want to add your own repository if you want to push code back and make pull requests.
I usually name the git remote for the main bonobo repository "upstream", and my own repository "origin".

.. code-block:: shell-session

    $ git remote rename origin upstream
    $ git remote add origin git@github.com:hartym/bonobo.git
    $ git fetch --all

Of course, replace my github username by the one you used to fork bonobo. You should be good to go!

Preview versions
----------------

Sometimes, there are pre-versions available (before a major release, for example). By default, pip does not target
pre-versions to avoid accidental upgrades to a potentially unstable version, but you can easily opt-in:

.. code-block:: shell-session

    $ pip install --upgrade --pre bonobo


Supported platforms
:::::::::::::::::::

Linux, OSX and other Unixes
---------------------------

Bonobo test suite runs continuously on Linux, and core developers use both OSX and Linux machines. Also, there are jobs
running on production linux machines everyday, so the support for those platforms should be quite excellent.

If you're using some esoteric UNIX machine, there can be surprises (although we're not aware, yet). We do not support
officially those platforms, but if you can actually fix the problems on those systems, we'll be glad to integrate
your patches (as long as it is tested, for both existing linux environments and your strange systems).

Windows
-------

Windows support is correct, as a few contributors helped us to test and fix the quirks.

There may still be minor issues on the windows platform, mostly due to the fact bonobo was not developed by windows
users.

We're trying to look into that but energy available to provide serious support on windows is very limited.

If you have experience in this domain and you're willing to help, you're more than welcome!
