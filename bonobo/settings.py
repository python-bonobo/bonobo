import logging
import os

from bonobo.errors import ValidationError


def to_bool(s):
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    if len(s):
        if s.lower() in ('f', 'false', 'n', 'no', '0'):
            return False
        return True
    return False


class Setting:
    __all__ = {}

    @classmethod
    def clear_all(cls):
        for setting in Setting.__all__.values():
            setting.clear()

    def __new__(cls, name, *args, **kwargs):
        Setting.__all__[name] = super().__new__(cls)
        return Setting.__all__[name]

    def __init__(self, name, default=None, validator=None, formatter=None):
        self.name = name

        if default is not None:
            self.default = default if callable(default) else lambda: default
        else:
            self.default = lambda: None

        self.validator = validator
        self.formatter = formatter

    def __repr__(self):
        return '<Setting {}={!r}>'.format(self.name, self.get())

    def __eq__(self, other):
        return self.get() == other

    def __bool__(self):
        return bool(self.get())

    def set(self, value):
        value = self.formatter(value) if self.formatter else value
        if self.validator and not self.validator(value):
            raise ValidationError(self, 'Invalid value {!r} for setting {}.'.format(value, self.name))
        self.value = value

    def set_if_true(self, value):
        """Sets the value to true if it is actually true. May sound strange but the main usage is enforcing some
        settings from command line."""
        if value:
            self.set(True)

    def get(self):
        try:
            return self.value
        except AttributeError:
            value = os.environ.get(self.name, None)
            if value is None:
                value = self.default()
            self.set(value)
            return self.value

    def clear(self):
        try:
            del self.value
        except AttributeError:
            pass


# Debug/verbose mode.
DEBUG = Setting('DEBUG', formatter=to_bool, default=False)

# Profile mode.
PROFILE = Setting('PROFILE', formatter=to_bool, default=False)

# Quiet mode.
QUIET = Setting('QUIET', formatter=to_bool, default=False)

# Logging level.
LOGGING_LEVEL = Setting(
    'LOGGING_LEVEL',
    formatter=logging._checkLevel,
    validator=logging._checkLevel,
    default=lambda: logging.DEBUG if DEBUG.get() else logging.INFO,
)

# Input/Output format for transformations
IOFORMAT_ARG0 = 'arg0'
IOFORMAT_KWARGS = 'kwargs'

IOFORMATS = {IOFORMAT_ARG0, IOFORMAT_KWARGS}

IOFORMAT = Setting('IOFORMAT', default=IOFORMAT_KWARGS, validator=IOFORMATS.__contains__)


def check():
    if DEBUG.get() and QUIET.get():
        raise RuntimeError('I cannot be verbose and quiet at the same time.')


clear_all = Setting.clear_all
