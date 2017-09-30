import logging
import sys
import textwrap
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING

from colorama import Fore, Style

from bonobo import settings
from bonobo.util.term import CLEAR_EOL

iswindows = (sys.platform == 'win32')


def get_format():
    yield '{b}[%(fg)s%(levelname)s{b}][{w}'
    yield '{b}][{w}'.join(('%(spent)04d', '%(name)s'))
    yield '{b}]'
    yield ' %(fg)s%(message)s{r}'
    if not iswindows:
        yield CLEAR_EOL


colors = {
    'b': '' if iswindows else Fore.BLACK,
    'w': '' if iswindows else Fore.LIGHTBLACK_EX,
    'r': '' if iswindows else Style.RESET_ALL,
}
format = (''.join(get_format())).format(**colors)


class Filter(logging.Filter):
    def filter(self, record):
        record.spent = record.relativeCreated // 1000
        if iswindows:
            record.fg = ''
        elif record.levelname == 'DEBG':
            record.fg = Fore.LIGHTBLACK_EX
        elif record.levelname == 'INFO':
            record.fg = Fore.LIGHTWHITE_EX
        elif record.levelname == 'WARN':
            record.fg = Fore.LIGHTYELLOW_EX
        elif record.levelname == 'ERR ':
            record.fg = Fore.LIGHTRED_EX
        elif record.levelname == 'CRIT':
            record.fg = Fore.RED
        else:
            record.fg = Fore.LIGHTWHITE_EX
        return True


class Formatter(logging.Formatter):
    def formatException(self, ei):
        tb = super().formatException(ei)
        if iswindows:
            return textwrap.indent(tb, ' | ')
        else:
            return textwrap.indent(tb, Fore.BLACK + ' | ' + Fore.WHITE)


def setup(level):
    logging.addLevelName(DEBUG, 'DEBG')
    logging.addLevelName(INFO, 'INFO')
    logging.addLevelName(WARNING, 'WARN')
    logging.addLevelName(ERROR, 'ERR ')
    logging.addLevelName(CRITICAL, 'CRIT')
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(Formatter(format))
    handler.addFilter(Filter())
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(level)


def set_level(level):
    logging.getLogger().setLevel(level)


def get_logger(name='bonobo'):
    return logging.getLogger(name)


# Compatibility with python logging
getLogger = get_logger

# Setup formating and level.
setup(level=settings.LOGGING_LEVEL.get())
