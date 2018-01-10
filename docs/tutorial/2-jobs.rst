Part 2: Writing ETL Jobs
========================

What's an ETL job ?
:::::::::::::::::::

In |bonobo|, an ETL job is a single graph that can be executed on its own.

Within a graph, each node are isolated and can only communicate using their
input and output queues. For each input row, a given node will be called with
the row passed as arguments. Each *return* or *yield* value will be put on the
node's output queue, and the nodes connected in the graph will then be able to
process it.

|bonobo| is a line-by-line data stream processing solution.

Handling the data-flow this way brings the following properties:

- **First in, first out**: unless stated otherwise, each node will receeive the
  rows from FIFO queues, and so, the order of rows will be preserved. That is
  true for each single node, but please note that if you define "graph bubbles"
  (where a graph diverge in different branches then converge again), the
  convergence node will receive rows FIFO from each input queue, meaning that
  the order existing at the divergence point wont stay true at the convergence
  point.

- **Parallelism**: each node run in parallel (by default, using independant
  threads). This is useful as you don't have to worry about blocking calls.
  If a thread waits for, let's say, a database, or a network service, the other
  nodes will continue handling data, as long as they have input rows available.

- **Independance**: the rows are independant from each other, making this way
  of working with data flows good for line-by-line data processing, but
  also not ideal for "grouped" computations (where an output depends on more
  than one line of input data). You can overcome this with rolling windows if
  the input required are adjacent rows, but if you need to work on the whole
  dataset at once, you should consider other software.

Graphs are defined using :class:`bonobo.Graph` instances, as seen in the
previous tutorial step.

What can be a node?
:::::::::::::::::::

**TL;DR**: … anything, as long as it’s callable().

Functions
---------

.. code-block:: python

    def get_item(id):
        return id, items.get(id)


Each node of a graph will be executed in isolation from the other nodes, and the data is passed from one node to the
next using FIFO queues, managed by the framework. It's transparent to the end-user, though, and you'll only use
function arguments (for inputs) and return/yield values (for outputs).

Each input row of a node will cause one call to this node's callable. Each output is cast internally as a tuple-like
data structure (or more precisely, a namedtuple-like data structure), and for one given node, each output row must
have the same structure.

If you return/yield something which is not a tuple, bonobo will create a tuple of one element.

Properties
----------

|bonobo| assists you with defining the data-flow of your data engineering process, and then streams data through your
callable graphs.

* Each node call will process one row of data.
* Queues that flows the data between node are first-in, first-out (FIFO) standard python :class:`queue.Queue`.
* Each node will run in parallel
* Default execution strategy use threading, and each node will run in a separate thread.

Fault tolerance
---------------

Node execution is fault tolerant.

If an exception is raised from a node call, then this node call will be aborted but bonobo will continue the execution
with the next row (after outputing the stack trace and incrementing the "err" counter for the node context).

It allows to have ETL jobs that ignore faulty data and try their best to process the valid rows of a dataset.

Some errors are fatal, though.

If you pass a 2 elements tuple to a node that takes 3 args, |bonobo| will raise an :class:`bonobo.errors.UnrecoverableTypeError`, and exit the
current graph execution as fast as it can (finishing the other node executions that are in progress first, but not
starting new ones if there are remaining input rows).


Let's write a sample data integration job
:::::::::::::::::::::::::::::::::::::::::

Let's create a sample application.

The goal of this application will be to extract all the fablabs in the world using an open-data API, normalize this
data and, for now, display it. We'll then build on this foundation in the next steps to write to files, databases, etc.





Moving forward
::::::::::::::

You now know:

* How to ...

**Next: :doc:`3-files`**
