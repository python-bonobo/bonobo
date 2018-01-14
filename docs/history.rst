History
=======

|bonobo| is a full rewrite of **rdc.etl**, aimed at modern python versions (3.5+).

**rdc.etl** is a now deprecated python 2.7+ ETL library for which development started in 2012, and was opensourced in
2013 (see `first commit <https://github.com/rdcli/rdc.etl/commit/fdbc11c0ee7f6b97322693bd0051d63677b06a93>`_).

Although the first commit in |bonobo| happened late 2016, it's based on a lot of code, learnings and experience that
happened because of **rdc.etl**.

It would have been counterproductive to migrate the same codebase:

  * a lot of mistakes were impossible to fix in a backward compatible way (for example, transformations were stateful,
    making them more complicated to write and impossible to reuse, a lot of effort was used to make the components have
    multi-inputs and multi-outputs, although in 99% of the case it's useless, etc.).
  * we also wanted to develop something that took advantage of modern python versions, hence the choice of 3.5+.

**rdc.etl** still runs data transformation jobs, in both python 2.7 and 3, and we reuse whatever is possible to
continue building |bonobo|.

