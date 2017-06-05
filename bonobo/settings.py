import os

import logging

from bonobo.errors import ValidationError


def to_bool(s):
    if len(s):
        if s.lower() in ('f', 'false', 'n', 'no', '0'):
            return False
        return True
    return False


# Debug/verbose mode.
DEBUG = to_bool(os.environ.get('DEBUG', 'f'))

# Profile mode.
PROFILE = to_bool(os.environ.get('PROFILE', 'f'))

# Quiet mode.
QUIET = to_bool(os.environ.get('QUIET', 'f'))

# Logging level.
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO

# Input/Output format for transformations
IOFORMAT_ARG0 = 'arg0'
IOFORMAT_KWARGS = 'kwargs'

IOFORMATS = {
    IOFORMAT_ARG0,
    IOFORMAT_KWARGS,
}

IOFORMAT = os.environ.get('IOFORMAT', IOFORMAT_KWARGS)


def validate_io_format(v):
    if callable(v):
        return v
    if v in IOFORMATS:
        return v
    raise ValidationError('Unsupported format {!r}.'.format(v))


def check():
    if DEBUG and QUIET:
        raise RuntimeError('I cannot be verbose and quiet at the same time.')

    if IOFORMAT not in IOFORMATS:
        raise RuntimeError('Invalid default input/output format.')

