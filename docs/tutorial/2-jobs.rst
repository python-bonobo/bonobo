Part 2: Writing ETL Jobs
========================

What's an ETL job ?
:::::::::::::::::::

- data flow, stream processing
- each node, first in first out
- parallelism

Each node has input rows, each row is one call, and each call has the input row passed as *args.

Each call can have outputs, sent either using return, or yield.

Each output row is stored internally as a tuple (or a namedtuple-like structure), and each output row must have the same structure (same number of fields, same len for tuple).

If you yield something which is not a tuple, bonobo will create a tuple of one element.

By default, exceptions are not fatal in bonobo. If a call raise an error, then bonobo will display the stack trace, increment the "err" counter for this node and move to the next input row.

Some errors are fatal, though. For example, if you pass a 2 elements tuple to a node that takes 3 args, bonobo will raise an UnrecoverableTypeError, and exit the current execution.

Let's write one
:::::::::::::::

We'll create a job to do the following

* Extract all the FabLabs from an open data API
* Apply a bit of formating
* Geocode the address and normalize it, if we can
* Display it (in the next step, we'll learn about writing the result to a file.





Moving forward
::::::::::::::

You now know:

* How to ...

**Next: :doc:`3-files`**
