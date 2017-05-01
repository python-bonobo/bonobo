Releases
========

WORK IN PROGRESS, THIS DOC IS UNFINISHED AND JUST RAW NOTES TO HELP ME RELEASING STUFF.

How to make a patch release?
::::::::::::::::::::::::::::

For now, reference at http://rdc.li/r

Additional checklist:

* make format

How to make a minor or major release?
:::::::::::::::::::::::::::::::::::::

Releases above patch level are more complex, because we did not find a way not to hardcode the version number in a bunch
of files, and because a few dependant services (source control, continuous integration, code coverage, documentation
builder ...) also depends on version numbers.

Checklist:

* Files
* Github


Recipes
:::::::

Get current minor::

    git semver | python -c 'import sys; print(".".join(sys.stdin.read().strip().split(".")[0:2]))'

Open git with all files containing current minor::

    ack `git semver | python -c 'import sys; print("\\\\.".join(sys.stdin.read().strip().split(".")[0:2]))'` | vim -

