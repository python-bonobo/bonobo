import sys
from textwrap import indent

from bonobo import settings
from bonobo.structs.bags import ErrorBag


def is_error(bag):
    return isinstance(bag, ErrorBag)


def _get_error_message(exc):
    if hasattr(exc, '__str__'):
        message = str(exc)
        return message[0].upper() + message[1:]
    return '\n'.join(exc.args),


def print_error(exc, trace, context=None, method=None):
    """
    Error handler. Whatever happens in a plugin or component, if it looks like an exception, taste like an exception
    or somehow make me think it is an exception, I'll handle it.

    :param exc: the culprit
    :param trace: Hercule Poirot's logbook.
    :return: to hell
    """

    from colorama import Fore, Style

    prefix = '{}{} | {}'.format(Fore.RED, Style.BRIGHT, Style.RESET_ALL)

    print(
        Style.BRIGHT,
        Fore.RED,
        type(exc).__name__,
        ' (in {}{})'.format(type(context).__name__, '.{}()'.format(method) if method else '') if context else '',
        Style.RESET_ALL,
        '\n',
        indent(_get_error_message(exc), prefix + Style.BRIGHT),
        Style.RESET_ALL,
        sep='',
        file=sys.stderr,
    )
    print(prefix, file=sys.stderr)
    print(indent(trace, prefix, predicate=lambda line: True), file=sys.stderr)
