----

Roadmap (in progress)
:::::::::::::::::::::

Bonobo is young. This roadmap is alive, and will evolve. Its only purpose is to
write down incoming things somewhere.

Version 0.2
-----------

* Changelog
* Migration guide
* Update documentation
* Threaded does not terminate anymore (fixed ?)
* More tests

Bugs:

- KeyboardInterrupt does not work anymore. (fixed ?)
- ThreadPool does not stop anymore. (fiexd ?)

Configuration
.............

* Support for position arguments (options), required options are good candidates.

Context processors
..................

* Be careful with order, especially with python 3.5. (done)
* @contextual decorator is not clean enough. Once the behavior is right, find a
  way to use regular inheritance, without meta.
* ValueHolder API not clean. Find a better way.

Random thoughts and things to do
................................

* Class-tree for Graph and Nodes

* Class-tree for execution contexts:

  * GraphExecutionContext
  * NodeExecutionContext
  * PluginExecutionContext

* Class-tree for ExecutionStrategies

  * NaiveStrategy
  * PoolExecutionStrategy
    * ThreadPoolExecutionStrategy
    * ProcessPoolExecutionStrategy
  * ThreadExecutionStrategy
  * ProcessExecutionStrategy

* Class-tree for bags

  * Bag
  * ErrorBag
  * InheritingBag

* Co-routines: for unordered, or even ordered but long io.

* "context processors": replace initialize/finalize by a generator that yields only once


* "execute" function:

    .. code-block:: python

        def execute(graph: Graph, *, strategy: ExecutionStrategy, plugins: List[Plugin]) -> Execution:
            pass

* Handling console. Can we use a queue, and replace stdout / stderr ?




