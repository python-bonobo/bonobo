Part 3: Working with Files
==========================

.. include:: _wip_note.rst

Writing to the console is nice, but using files is probably more realistic.

Let's see how to use a few builtin writers and both local and remote filesystems.


Filesystems
:::::::::::

In |bonobo|, files are accessed within a **filesystem** service which must be something with the same interface as
`fs' FileSystem objects <https://docs.pyfilesystem.org/en/latest/builtin.html>`_. As a default, you'll get an instance
of a local filesystem mapped to the current working directory as the `fs` service. You'll learn more about services in
the next step, but for now, let's just use it.


Writing using the service
:::::::::::::::::::::::::

Although |bonobo| contains helpers to write to common file formats, let's start by writing it manually.

.. code-block:: python

    from bonobo.config import use
    from bonobo.constants import NOT_MODIFIED

    @use('fs')
    def write_repr_to_file(*row, fs):
        with fs.open('output.txt', 'a+') as f:
            print(row, file=f)
        return NOT_MODIFIED

Then, update the `get_graph(...)` function, by adding `write_repr_to_file` just before your `PrettyPrinter()` node.

Let's try to run that and think about what happens.

Each time a row comes to this node, the output file is open in "append or create" mode, a line is written, and the file
is closed.

This is **NOT** how you want to do things. Let's rewrite it so our `open(...)` call becomes execution-wide.





* Filesystems

* Reading files

* Writing files

* Writing files to S3

* Atomic writes ???


Moving forward
::::::::::::::

You now know:

* How to ...

It's now time to jump to :doc:`4-services`.
