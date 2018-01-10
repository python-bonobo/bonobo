Part 5: Projects and Packaging
==============================

.. include:: _wip_note.rst

Until then, we worked with one file managing a job.

Real life often involves more complicated setups, with relations and imports between different files.

This section will describe the options available to move this file into a package, either a new one or something
that already exists in your own project.

Data processing is something a wide variety of tools may want to include, and thus |bonobo| does not enforce any
kind of project structure, as the targert structure will be dicated by the hosting project. For example, a `pipelines`
sub-package would perfectly fit a django or flask project, or even a regular package, but it's up to you to chose the
structure of your project.

 is about set of jobs working together within a project.

Let's see how to move from the current status to a package.


Moving forward
::::::::::::::

You now know:

* How to ...

That's the end of the tutorial, you should now be familiar with all the basics.

A few appendixes to the tutorial can explain how to integrate with other systems (we'll use the "fablabs" application
created in this tutorial and extend it):

* :doc:`notebooks`
* :doc:`sqlalchemy`
* :doc:`django`
* :doc:`docker`

Then, you can either to jump head-first into your code, or you can have a better grasp at all concepts by
:doc:`reading the full bonobo guide </guide/index>`.

Happy data flows!


