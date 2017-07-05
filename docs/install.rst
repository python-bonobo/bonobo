Installation
============

Create an ETL project
:::::::::::::::::::::

Creating a project and starting to write code should take less than a minute:

.. code-block:: shell-session

    $ pip install --upgrade bonobo cookiecutter
    $ bonobo init my-etl-project
    $ bonobo run my-etl-project

Once you bootstrapped a project, you can start editing the default example transformation by editing
`my-etl-project/main.py`.

Other installation options
::::::::::::::::::::::::::

Install from PyPI
-----------------

You can install it directly from the `Python Package Index <https://pypi.python.org/pypi/bonobo>`_ (like we did above).

.. code-block:: shell-session

    $ pip install bonobo

Install from source
-------------------

If you want to install an unreleased version, you can use git urls with pip. This is useful when using bonobo as a
dependency of your code and you want to try a forked version of bonobo with your software. You can use a `git+http`
string in your `requirements.txt` file. However, the best option for development on bonobo is an editable install (see
below).

.. code-block:: shell-session

    $ pip install git+https://github.com/python-bonobo/bonobo.git@develop#egg=bonobo

Editable install
----------------

If you plan on making patches to Bonobo, you should install it as an "editable" package, which is a really great pip
feature. Pip will clone your repository in a source directory and create a symlink for it in the site-package directory
of your python interpreter.

.. code-block:: shell-session

    $ pip install --editable git+https://github.com/python-bonobo/bonobo.git@master#egg=bonobo

.. note:: You can also use the `-e` flag instead of the long version.

If you can't find the "source" directory, try trunning this:

.. code-block:: shell-session

    $ python -c "import bonobo; print(bonobo.__path__)"

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

Windows support
:::::::::::::::

There are minor issues on the windows platform, mostly due to the fact bonobo was not developed by experienced windows
users.

We're trying to look into that but energy available to provide serious support on windows is very limited.

If you have experience in this domain and you're willing to help, you're more than welcome!

