Debugging
=========

.. note::

    This document writing is in progress, but its content should be correct (but succint).

Using a debugger (pdb...)
:::::::::::::::::::::::::

Using a debugger works (as in any python piece of code), but you must be aware that each node runs in a separate thread,
which means a few things:

* If a breakpoint happens in a thread, then this thread will stop, but all other threads will continue running. This
  can be especially annoying if you try to use the pdb REPL for example, as your prompt will be overriden a few
  times/second by the current excution statistics.

  To avoid that, you can run bonobo with `QUIET=1` in environment, to hide statistics.

* If your breakpoint never happens (although it's at the very beginning of your transformation), it may mean that
  something happens out of the transform. The :class:`bonobo.execution.contexts.NodeExecutionContext` instance that
  surrounds your transformation may be stuck in its `while True: transform()` loop.

  Break one level higher


Using printing statements
:::::::::::::::::::::::::

Of course, you can :obj:`print` things.

You can even add :obj:`print` statements in graphs, to :obj:`print` once per row.

A better :obj:`print` is available though, suitable for both flow-based data processing and human eyes.
Check :class:`bonobo.PrettyPrinter`.


Inspecting graphs
:::::::::::::::::

* Using the console: `bonobo inspect --graph`.
* Using Jupyter notebook: install the extension and just display a graph.


.. include:: _next.rst
