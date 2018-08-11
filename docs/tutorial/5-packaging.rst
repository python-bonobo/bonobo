Part 5: Projects and Packaging
==============================

Throughout this tutorial, we have been working with one file managing a job but real life often involves more complicated setups, with relations and imports between different files.

Data processing is something a wide variety of tools may want to include, and thus |bonobo| does not enforce any
kind of project structure, as the target structure will be dictated by the hosting project. For example, a `pipelines`
sub-package would perfectly fit a django or flask project, or even a regular package, but it's up to you to chose the
structure of your project.


Imports mechanism
:::::::::::::::::

|bonobo| does not enforce anything on how the python import mechanism work. Especially, it won't add anything to your
`sys.path`, unlike some popular projects, because we're not sure that's something you want.

If you want to use imports, you should move your script into a python package, and it's up to you to have it setup
correctly.


Moving into an existing project
:::::::::::::::::::::::::::::::

First, and quite popular option, is to move your ETL job file into a package that already exists.

For example, it can be your existing software, eventually using some frameworks like django, flask, twisted, celery...
Name yours!

We suggest, but nothing is compulsory, that you decide on a namespace that will hold all your ETL pipelines and move all
your jobs in it. For example, it can be `mypkg.pipelines`.


Creating a brand new package
::::::::::::::::::::::::::::

Because you may be starting a project involving some data-engineering, you may not have a python package yet. As
it can be a bit tedious to setup right, there is a helper, using `Medikit <http://medikit.rdc.li/en/latest/>`_, that
you can use to create a brand new project:

.. code-block:: shell-session

    $ bonobo init --package pipelines

Answer a few questions, and you should now have a `pipelines` package, with an example transformation in it.

You can now follow the instructions on how to install it (`pip install --editable pipelines`), and the import mechanism
will work "just right" in it.


Common stuff
::::::::::::

Probably, you'll want to separate the `get_services()` factory from your pipelines, and just import it, as the
dependencies may very well be project wide.

But hey, it's just python! You're at home, now!


Moving forward
::::::::::::::

That's the end of the tutorial, you should now be familiar with all the basics.

A few appendixes to the tutorial can explain how to integrate with other systems (we'll use the "fablabs" application
created in this tutorial and extend it):

* :doc:`/extension/django`
* :doc:`/extension/docker`
* :doc:`/extension/jupyter`
* :doc:`/extension/sqlalchemy`

Then, you can either jump head-first into your code, or you can have a better grasp at all concepts by
:doc:`reading the full bonobo guide </guide/index>`.

You should also `join the slack community <https://bonobo-slack.herokuapp.com/>`_ and ask all your questions there! No
need to stay alone, and the only stupid question is the one nobody asks!

Happy data flows!


