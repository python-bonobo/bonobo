Contributing
============

There's a lot of different ways you can contribute, and not all of them includes coding. Do not think that the codeless
contributions have less value, all contributions are very important.

* You can contribute to the documentation.
* You can help reproducing errors and giving more infos in the issues.
* You can open issues with problems you're facing.
* You can help creating better presentation material.
* You can talk about it in your local python user group.
* You can enhance examples.
* You can enhance tests.
* etc.

tl;dr
:::::

1. Fork the github repository

.. code-block:: shell-session

    $ git clone https://github.com/python-bonobo/bonobo.git  # change this to use your fork.
    $ cd bonobo
    $ git remote add upstream https://github.com/python-bonobo/bonobo.git
    $ git fetch upstream
    $ git checkout upstream/develop -b feature/my_awesome_feature
    $ # code, code, code, test, doc, code, test ...
    $ git commit -m '[topic] .... blaaaah ....'
    $ git push origin feature/my_awesome_feature

2. Open pull request
3. Rince, repeat


Code-related contributions (including tests and examples)
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::

Contributing to bonobo is usually done this way:

* Discuss ideas in the `issue tracker <https://github.com/python-bonobo/bonobo>`_ or on `Slack <https://bonobo-slack.herokuapp.com/>`_.
* Fork the `repository <https://github.com/python-bonobo>`_.
* Think about what happens for existing userland code if your patch is applied.
* Open pull request early with your code to continue the discussion as you're writing code.
* Try to write simple tests, and a few lines of documentation.

Although we don't have a complete guide on this topic for now, the best way is to fork
the github repository and send pull requests.

Tools
:::::

Issues: https://github.com/python-bonobo/bonobo/issues

Roadmap: https://www.bonobo-project.org/roadmap

Slack: https://bonobo-slack.herokuapp.com/

Guidelines
::::::::::

* We tend to use `semantic versioning <http://semver.org/>`_. This should be 100% true once we reach 1.0, but until then we will fail
  and learn. Anyway, the user effort for each BC-break is a real pain, and we want to keep that in mind.
* The 1.0 milestone has one goal: create a solid foundation we can rely on, in term of API. To reach that, we want to keep it as
  minimalist as possible, considering only a few userland tools as the public API.
* Said simplier, the core should stay as light as possible.
* Let's not fight over coding standards. We enforce it using `yapf <https://github.com/google/yapf#yapf>`_, and a `make format` call
  should reformat the whole codebase for you. We encourage you to run it before making a pull request, and it will be run before each
  release anyway, so we can focus on things that have value instead of details.
* Tests are important. One obvious reason is that we want to have a stable and working system, but one less obvious reason is that
  it forces better design, making sure responsibilities are well separated and scope of each function is clear. More often than not,
  the "one and only obvious way to do it" will be obvious once you write the tests.
* Documentation is important. It's the only way people can actually understand what the system do, and userless software is pointless.
  One book I read a long time ago said that half the energy spent building something should be devoted to explaining what and why you're
  doing something, and that's probably one of the best advice I read about (although, as every good piece of advice, it's more easy to
  repeat than to apply).

License
:::::::

`Bonobo is released under the apache license <https://www.bonobo-project.org/license>`_.

License for non lawyers
:::::::::::::::::::::::

Use it, change it, hack it, brew it, eat it.

For pleasure, non-profit, profit or basically anything else, except stealing credit.

Provided without any warranty.


