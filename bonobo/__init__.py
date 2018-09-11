# Bonobo data-processing toolkit.
#
# Bonobo is a line-by-line data-processing toolkit for python 3.5+ emphasizing simplicity and atomicity of data
# transformations using a simple directed graph of python callables.
#
# Licensed under Apache License 2.0, read the LICENSE file in the root of the source tree.

import sys

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
__logo__ = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" x="0px" y="0px" viewBox="0 0 100 100" enable-background="new 0 0 100 100" xml:space="preserve"><g><path d="M21.52,65.909c1.685,0,3.297-0.314,4.784-0.884c0.345,1.537,0.656,3.199,0.931,4.979c0.863,5.595,1.048,10.371,1.05,10.419   l0.02,0.535l0.291,0.449c1.407,2.177,3.333,4.029,5.724,5.505c1.889,1.166,4.074,2.102,6.495,2.781   c4.106,1.151,7.602,1.21,8.261,1.21c0.05,0,0.067,0,0.117,0c0.659,0,4.155-0.058,8.261-1.21c2.421-0.679,4.606-1.614,6.495-2.781   c2.391-1.476,4.317-3.329,5.725-5.506l0.291-0.449l0.02-0.535c0.002-0.047,0.183-4.788,1.043-10.379   c0.274-1.782,0.585-3.447,0.929-4.985c1.462,0.549,3.044,0.85,4.695,0.85c7.383,0,13.39-6.007,13.39-13.39   c0-5.475-3.303-10.192-8.021-12.265c0.717-4.397,0.345-8.47-1.11-11.925c-1.449-3.441-3.948-6.288-7.428-8.461   c-3.387-2.116-7.75-3.608-12.99-4.444c0.099-0.447,0.18-0.742,0.181-0.747l0.813-2.947l-3.013,0.513   c-1.75,0.298-3.086,0.987-4.059,1.708c0.224-0.638,0.485-1.233,0.698-1.647l1.745-3.363l-3.749,0.543   c-5.216,0.755-7.91,3.472-9.155,5.278c-7.073,0.432-12.901,1.8-17.336,4.07c-4.223,2.162-7.248,5.157-8.994,8.901   c-1.666,3.575-2.131,7.842-1.381,12.481C11.475,42.267,8.13,47.01,8.13,52.519C8.13,59.902,14.136,65.909,21.52,65.909z    M21.147,29.377c1.371-2.942,3.807-5.324,7.241-7.083c4.152-2.126,9.797-3.372,16.779-3.703l1.107-0.053l0.519-0.979   c0.388-0.733,1.371-2.176,3.462-3.206c-0.177,0.798-0.28,1.635-0.223,2.422l0.125,1.727l1.73,0.076   c0.219,0.01,0.569,0.02,0.939,0.03c0.492,0.014,1.105,0.031,1.364,0.048l1.006,0.064l0.632-0.786   c0.105-0.13,0.24-0.283,0.409-0.445l-0.142,1.275l1.908,0.235c10.328,1.271,16.829,4.918,19.323,10.839   c1.244,2.953,1.383,6.228,0.917,9.386c-0.193,1.304-0.488,2.589-0.853,3.822c-1.182,3.998-3.082,7.46-4.507,9.33   c-1.236,1.623-2.323,3.808-3.255,6.534c-0.109,0.32-0.217,0.648-0.322,0.983c-0.041,0.131-0.082,0.261-0.122,0.394   c-0.267,0.88-0.52,1.811-0.758,2.79c-0.471,1.935-0.886,4.061-1.242,6.376c-0.729,4.737-0.986,8.81-1.06,10.264   c-5.086,7.213-16.44,7.297-16.93,7.297l-0.059,0l-0.059,0c-0.49,0-11.844-0.084-16.93-7.297c-0.074-1.455-0.332-5.528-1.06-10.264   c-0.36-2.341-0.78-4.487-1.258-6.44c-0.37-1.512-0.774-2.906-1.213-4.181c-0.926-2.69-2.004-4.848-3.228-6.456   c-1.443-1.894-3.339-5.352-4.515-9.336c-0.365-1.235-0.661-2.521-0.852-3.827C19.531,35.895,19.716,32.447,21.147,29.377z    M86.151,52.519c0,5.239-4.262,9.501-9.501,9.501c-1.275,0-2.493-0.253-3.605-0.711c0.684-0.979,1.83-2.531,3.165-3.968   c2.648-2.851,4.356-3.454,5.013-3.105l1.824-3.434c-0.98-0.521-2.535-0.901-4.609-0.031c0.99-1.894,1.956-4.156,2.687-6.631   C84.114,45.743,86.151,48.897,86.151,52.519z M17.128,44.096c0.772,2.631,1.811,5.024,2.865,6.992   c-2.412-1.265-4.196-0.861-5.28-0.286l1.824,3.434c0.654-0.347,2.351,0.249,4.983,3.073c1.401,1.503,2.605,3.148,3.283,4.126   c-1.024,0.378-2.13,0.585-3.284,0.585c-5.239,0-9.501-4.262-9.501-9.501C12.018,48.863,14.094,45.684,17.128,44.096z"></path><path d="M25.232,39.91c1.274,2.821,3.681,5.648,7.155,8.404c0.794,0.63,1.563,1.233,2.307,1.81   c1.346,1.043,2.608,1.998,3.777,2.857c-0.103,0.144-0.206,0.288-0.312,0.433c-1.032,1.429-2.099,2.906-2.86,5.691   c-0.791,2.895-1.16,6.918-1.16,12.658v0.153l0.024,0.152c0.044,0.274,0.486,2.751,2.574,5.239c1.91,2.276,5.611,4.989,12.396,4.989   s10.486-2.713,12.396-4.989c2.088-2.488,2.53-4.965,2.574-5.239l0.024-0.152v-0.153c0-5.714-0.371-9.728-1.167-12.632   c-0.764-2.786-1.833-4.28-2.867-5.726c-0.102-0.142-0.202-0.282-0.301-0.422c1.137-0.836,2.363-1.762,3.668-2.772   c0.779-0.603,1.585-1.235,2.419-1.897c3.474-2.756,5.881-5.583,7.155-8.404c0.048-0.107,0.095-0.214,0.14-0.322   c1.08-2.566,1.22-5.153,0.401-7.502c-0.877-2.516-2.776-4.657-5.492-6.193c-2.443-1.382-5.366-2.143-8.229-2.143H38.413   c-2.863,0-5.786,0.761-8.229,2.143c-2.716,1.536-4.615,3.678-5.492,6.193c-0.822,2.358-0.677,4.955,0.413,7.531   C25.146,39.715,25.188,39.812,25.232,39.91z M38.413,27.639h21.441c4.591,0,8.911,2.462,10.049,5.727   c1.196,3.431-1.091,7.658-6.44,11.901c-2.821,2.238-5.324,4.137-7.439,5.644l-1.449,1.032l0.9,1.535   c0.501,0.854,0.987,1.533,1.457,2.19c0.949,1.327,1.699,2.375,2.279,4.491c0.604,2.203,0.937,5.376,1.012,9.66H38.044   c0.074-4.308,0.405-7.49,1.006-9.689c0.575-2.104,1.319-3.134,2.262-4.439c0.455-0.63,0.971-1.344,1.48-2.213l0.9-1.535   l-1.449-1.032c-2.115-1.507-4.618-3.406-7.439-5.644c-5.349-4.243-7.636-8.47-6.44-11.901   C29.501,30.101,33.822,27.639,38.413,27.639z M58.55,74.807c-2.004,2.389-5.173,3.6-9.417,3.6c-4.157,0-7.286-1.164-9.298-3.461   c-0.367-0.419-0.663-0.841-0.903-1.24h20.401C59.121,74.061,58.863,74.434,58.55,74.807z"></path><path d="M41.182,45.137c2.76,0,5.006-2.245,5.006-5.006c0-2.76-2.245-5.005-5.006-5.005c-2.76,0-5.005,2.245-5.005,5.005   C36.177,42.892,38.422,45.137,41.182,45.137z M41.182,39.015c0.616,0,1.117,0.501,1.117,1.117c0,0.616-0.501,1.117-1.117,1.117   c-0.616,0-1.117-0.501-1.117-1.117C40.065,39.516,40.566,39.015,41.182,39.015z"></path><path d="M57.084,45.137c2.76,0,5.005-2.245,5.005-5.006c0-2.76-2.245-5.005-5.005-5.005c-2.76,0-5.006,2.245-5.006,5.005   C52.079,42.892,54.324,45.137,57.084,45.137z M57.084,39.015c0.616,0,1.117,0.501,1.117,1.117c0,0.616-0.501,1.117-1.117,1.117   c-0.616,0-1.117-0.501-1.117-1.117C55.967,39.516,56.468,39.015,57.084,39.015z"></path><path d="M43.061,60.577c0,0,4.707-0.937,3.347-4.917C46.408,55.659,42.328,57.448,43.061,60.577z"></path><path d="M55.205,60.577c0.732-3.128-3.347-4.917-3.347-4.917C50.499,59.64,55.205,60.577,55.205,60.577z"></path></g></svg>'
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


del sys
