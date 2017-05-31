import os

import logging


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


def check():
    if DEBUG and QUIET:
        raise RuntimeError('I cannot be verbose and quiet at the same time.')
