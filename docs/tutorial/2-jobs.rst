Part 2: Writing ETL Jobs
========================

What's an ETL job ?
:::::::::::::::::::

In |bonobo|, an ETL job is a formal definition of an executable graph.

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
