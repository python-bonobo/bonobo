import os


def to_bool(s):
    if len(s):
        if s.lower() in ('f', 'false', 'n', 'no', '0'):
            return False
        return True
    return False


# Debug mode.
DEBUG = to_bool(os.environ.get('BONOBO_DEBUG', 'f'))

# Profile mode.
PROFILE = to_bool(os.environ.get('BONOBO_PROFILE', 'f'))
