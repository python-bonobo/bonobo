"""
This package is considered private, and should only be used within bonobo.

"""

import json

import bonobo
from bonobo.util.collections import tuplize
from bonobo.util.python import WorkingDirectoryModulesRegistry


def _parse_option(option):
    """
    Parse a 'key=val' option string into a python (key, val) pair

    :param option: str
    :return: tuple
    """
    try:
        key, val = option.split('=', 1)
    except ValueError:
        return option, True

    try:
        val = json.loads(val)
    except json.JSONDecodeError:
        pass

    return key, val


def _resolve_options(options=None):
    """
    Resolve a collection of option strings (eventually coming from command line) into a python dictionary.

    :param options: tuple[str]
    :return: dict
    """
    if options:
        return dict(map(_parse_option, options))
    return dict()


@tuplize
def _resolve_transformations(transformations):
    """
    Resolve a collection of strings into the matching python objects, defaulting to bonobo namespace if no package is provided.

    Syntax for each string is path.to.package:attribute

    :param transformations: tuple(str)
    :return: tuple(object)
    """
    registry = WorkingDirectoryModulesRegistry()
    for t in transformations:
        try:
            mod, attr = t.split(':', 1)
            yield getattr(registry.require(mod), attr)
        except ValueError:
            yield getattr(bonobo, t)
