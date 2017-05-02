Changelog
=========

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
