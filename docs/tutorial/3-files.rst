Part 3: Working with Files
==========================

Writing to the console is nice, but let's be serious, real world will require us to use files or external services.

Let's see how to use a few builtin writers and both local and remote filesystems.


Filesystems
:::::::::::

In |bonobo|, files are accessed within a **filesystem** service (a `fs' FileSystem object
<https://docs.pyfilesystem.org/en/latest/builtin.html>`_).

As a default, you'll get an instance of a local filesystem mapped to the current working directory as the `fs` service.
You'll learn more about services in the next step, but for now, let's just use it.


Writing to files
::::::::::::::::

To write in a file, we'll need to have an open file handle available during the whole transformation life.

We'll use a context processor to do so. A context processor is something very much like a
:obj:`contextlib.contextmanager`, that |bonobo| will use to run a setup/teardown logic on objects that need to have
the same lifecycle as a job execution.

Let's write one that just handle opening and closing the file:

.. code-block:: python

    def with_opened_file(self, context):
        with open('output.txt', 'w+') as f:
            yield f

Now, we need to write a `writer` transformation, and apply this context processor on it:

.. code-block:: python

    from bonobo.config import use_context_processor

    @use_context_processor(with_opened_file)
    def write_repr_to_file(f, *row):
        f.write(repr(row) + "\n")

The `f` parameter will contain the value yielded by the context processors, in order of appearance. You can chain
multiple context processors. To find out about how to implement this, check the |bonobo| guides in the documentation.

Please note that the :func:`bonobo.config.use_context_processor` decorator will modify the function in place, but won't
modify its behaviour. If you want to call it out of the |bonobo| job context, it's your responsibility to provide
the right parameters (and here, the opened file).

To run this, change the last stage in the pipeline in get_graph to write_repr_to_file

.. code-block:: python

    def get_graph(**options):
        graph = bonobo.Graph()
        graph.add_chain(
            extract_fablabs,
            bonobo.Limit(10),
            write_repr_to_file,
        )
        return graph

Now run tutorial.py and check the output.txt file.


Using the filesystem
::::::::::::::::::::

We opened the output file using a hardcoded filename and filesystem implementation. Writing flexible jobs include the
ability to change the load targets at runtime, and |bonobo| suggest to use the `fs` service to achieve this with files.

Let's rewrite our context processor to use it.

.. code-block:: python

    def with_opened_file(self, context):
        with context.get_service('fs').open('output.txt', 'w+') as f:
            yield f

The interface does not change much, but this small change allows the end-user to change the filesystem implementation at
runtime, which is great for handling different environments (local development, staging servers, production, ...).

Note that |bonobo| only provides very few services with default implementation (actually, only `fs` and `http`), but
you can define all the services you want, depending on your system. You'll learn more about this in the next tutorial
chapter.


Using a different filesystem
::::::::::::::::::::::::::::

To change the `fs` implementation, you need to provide your implementation in the dict returned by `get_services()`.

Let's write to a remote location, which will be an Amazon S3 bucket. First, we need to install the driver:

.. code-block:: shell-session

    pip install fs-s3fs

Then, just provide the correct bucket to :func:`bonobo.open_fs`:

.. code-block:: python

    def get_services(**options):
        return {
            'fs': bonobo.open_fs('s3://bonobo-examples')
        }

.. note::

    You must provide a bucket for which you have the write permission, and it's up to you to setup your amazon
    credentials in such a way that `boto` can access your AWS account.


Using builtin writers
:::::::::::::::::::::

Until then, and to have a better understanding of what happens, we implemented our writers ourselves.

|bonobo| contains writers for a variety of standard file formats, and you're probably better off using builtin writers.

Let's use a :obj:`bonobo.CsvWriter` instance instead, by replacing our custom transformation in the graph factory
function:

.. code-block:: python

    def get_graph(**options):
        graph = bonobo.Graph()
        graph.add_chain(
            ...
            bonobo.CsvWriter('output.csv'),
        )
        return graph

Reading from files
::::::::::::::::::

Reading from files is done using the same logic as writing, except that you'll probably have only one call to a reader. You can read the file we just wrote by using a :obj:`bonobo.CsvReader` instance:

.. code-block:: python

    def get_graph(**options):
        graph = bonobo.Graph()
        graph.add_chain(
            bonobo.CsvReader('input.csv'),
            ...
        )
        return graph


Moving forward
::::::::::::::

You now know:

* How to use the filesystem (`fs`) service.
* How to read from files.
* How to write to files.
* How to substitute a service at runtime.

It's now time to jump to :doc:`4-services`.

