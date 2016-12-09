Changelog
=========


0.9.0
:::::

* todo migrate doc
* todo migrate tests
* todo migrate transforms ?

Initial release
:::::::::::::::

* Migration from rdc.etl.
* New cool name.
* Only supports python 3.5+, aggressively (which means, we can use async, and we remove all things from python 2/six compat)
* Removes all thing deprecated and/or not really convincing
* We want transforms to be simple callables, so refactoring of the harness mess
* We want to use plain python data structures, so hashes are removed. If you use python 3.6, you may even get sorted dicts.
* Input/output MUX DEMUX removed, maybe no need for that in the real world. May come back, but not in 1.0
* Change dependency policy. We need to include only the very basic requirements (and very required). Everything related to transforms that we may not use (bs, sqla, ...) should be optional dependencies.
* execution strategies !!!