# Bonobo data-processing toolkit.
#
# Bonobo is a line-by-line data-processing toolkit for python 3.5+ emphasizing simplicity and atomicity of data
# transformations using a simple directed graph of python callables.
#
# Licensed under Apache License 2.0, read the LICENSE file in the root of the source tree.

import sys
from pathlib import Path

if sys.version_info < (3, 5):
    raise RuntimeError("Python 3.5+ is required to use Bonobo.")

from bonobo._api import (
    run,
    inspect,
    Graph,
    create_strategy,
    open_fs,
    CsvReader,
    CsvWriter,
    FileReader,
    FileWriter,
    Filter,
    FixedWindow,
    Format,
    JsonReader,
    JsonWriter,
    LdjsonReader,
    LdjsonWriter,
    Limit,
    OrderFields,
    PickleReader,
    PickleWriter,
    PrettyPrinter,
    RateLimited,
    Rename,
    SetFields,
    Tee,
    UnpackItems,
    MapFields,
    count,
    identity,
    noop,
    create_reader,
    create_writer,
    get_examples_path,
    open_examples_fs,
    get_argument_parser,
    parse_args,
    __all__,
    __doc__,
)
from bonobo._version import __version__

__all__ = ["__version__"] + __all__
with (Path(__file__).parent / "bonobo.svg").open() as f:
    __logo__ = f.read()
__doc__ = __doc__
__version__ = __version__


def _repr_html_():
    """This allows to easily display a version snippet in Jupyter."""
    from bonobo.commands.version import get_versions

    return (
        '<div style="padding: 8px;">'
        '  <div style="float: left; width: 20px; height: 20px;">{}</div>'
        '  <pre style="white-space: nowrap; padding-left: 8px">{}</pre>'
        "</div>"
    ).format(__logo__, "<br/>".join(get_versions(all=True)))


del sys, Path, f
