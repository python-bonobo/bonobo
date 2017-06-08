import logging
import os

from bonobo.errors import ValidationError


def to_bool(s):
    if len(s):
        if s.lower() in ('f', 'false', 'n', 'no', '0'):
            return False
        return True
    return False


class Setting:
    def __init__(self, name, default=None, validator=None):
        self.name = name

        if default:
            self.default = default if callable(default) else lambda: default
        else:
            self.default = lambda: None

        if validator:
            self.validator = validator
        else:
            self.validator = None

    def __repr__(self):
        return '<Setting {}={!r}>'.format(self.name, self.value)

    def set(self, value):
        if self.validator and not self.validator(value):
            raise ValidationError('Invalid value {!r} for setting {}.'.format(value, self.name))
        self.value = value

    def get(self):
        try:
            return self.value
        except AttributeError:
            self.value = self.default()
            return self.value


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

IOFORMAT = Setting('IOFORMAT', default=IOFORMAT_KWARGS, validator=IOFORMATS.__contains__)


def check():
    if DEBUG and QUIET:
        raise RuntimeError('I cannot be verbose and quiet at the same time.')
