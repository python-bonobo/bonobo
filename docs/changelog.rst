Changelog
=========

v.0.3.0 - 22 may 2017
:::::::::::::::::::::

Features
--------

* ContextProcessors can now be implemented by getting the "yield" value (v = yield x), shortening the teardown-only context processors by one line.
* File related writers (file, csv, json ...) now returns NOT_MODIFIED, making it easier to chain something after.
* More consistent console output, nodes are now sorted in a topological order before display.
* Graph.add_chain(...) now takes _input and _output parameters the same way, accepting indexes, instances or names (subject to change).
* Graph.add_chain(...) now allows to "name" a chain, using _name keyword argument, to easily reference its output later (subject to change).
* New settings module (bonobo.settings) read environment for some global configuration stuff (DEBUG and PROFILE, for now).
* New Method subclass of Option allows to use Configurable objects as decorator (see bonobo.nodes.filter.Filter for a simple example).
* New Filter transformation in standard library.

Internal features
-----------------

* Better ContextProcessor implementation, avoiding to use a decorator on the parent class. Now works with Configurable instances like Option, Service and Method.
* ContextCurrifier replaces the logic that was in NodeExecutionContext, that setup and teardown the context stack. Maybe the name is not ideal.
* All builtin transformations are of course updated to use the improved API, and should be 100% backward compatible.
* The "core" package has been dismantled, and its rare remaining members are now in "structs" and "util" packages.
* Standard transformation library has been moved under the bonobo.nodes package. It does not change anything if you used bonobo.* (which you should).
* ValueHolder is now more restrictive, not allowing to use .value anymore.

Miscellaneous
-------------

* Code cleanup, dead code removal, more tests, etc.
* More documentation.

v.0.2.4 - 2 may 2017
::::::::::::::::::::

* Cosmetic release for PyPI package page formating. Same content as v.0.2.3.

v.0.2.3 - 1 may 2017
:::::::::::::::::::::

* Positional options now supported, backward compatible. All FileHandler subclasses supports their path argument as positional.
* Better transformation lifecycle management (still work needed here).
* Windows continuous integration now works.
* Refactoring the "API" a lot to have a much cleaner first glance at it.
* More documentation, tutorials, and tuning project artifacts.

v.0.2.2 - 28 apr 2017
:::::::::::::::::::::

* First implementation of services and basic injection.
* Default service configuration for directories and files.
* Code structure refactoring.
* Critical bug fix in default strategy causing end of pipeline not to terminate correctly.
* Force tighter dependency management to avoid unexpected upgrade problems.
* Filesystems are now injected as a service, using new filesystem2 (fs) dependency.

v.0.2.1 - 25 apr 2017
:::::::::::::::::::::

* Plugins (jupyter, console) are now auto-activated depending on the environment when using bonobo.run(...).
* Remove dependencies to toolz (which was unused) and blessings (which caused problems on windows).
* New dependency on colorama, which has better cross-platform support than blessings.
* New bonobo.structs package containing basic datastructures, like graphs, tokens and bags.
* Enhancements of ValueHolder to implement basic operators on its value without referencing the value attribute.
* Fix issue with timezone argument of OpenDataSoftAPI (Sanket Dasgupta).
* Fix Jupyter plugin.
* Better continuous integration, testing and fixes in documentation.
* Version updates for dependencies (psutil install problem on windows).

Initial release
:::::::::::::::

* Migration from rdc.etl.
* New cool name (ok, that's debatable).
* Only supports python 3.5+, aggressively (which means, we can use async, and we remove all things from python 2/six compat)
* Removes all thing deprecated and/or not really convincing from rdc.etl.
* We want transforms to be simple callables, so refactoring of the harness mess.
* We want to use plain python data structures, so hashes are removed. If you use python 3.6, you may even get sorted dicts.
* Input/output MUX DEMUX removed, maybe no need for that in the real world. May come back, but not in 1.0
* Change dependency policy. We need to include only the very basic requirements (and very required). Everything related
  to transforms that we may not use (bs, sqla, ...) should be optional dependencies.
* Execution strategies, threaded by default.
