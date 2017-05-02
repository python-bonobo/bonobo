import sys

from bonobo.structs.bags import ErrorBag


def is_error(bag):
    return isinstance(bag, ErrorBag)


def print_error(exc, trace, context=None, prefix=''):
    """
    Error handler. Whatever happens in a plugin or component, if it looks like an exception, taste like an exception
    or somehow make me think it is an exception, I'll handle it.

    :param exc: the culprit
    :param trace: Hercule Poirot's logbook.
    :return: to hell
    """

    from colorama import Fore, Style
    print(
        Style.BRIGHT,
        Fore.RED,
        '\U0001F4A3 {}{}{}'.format(
            (prefix + ': ') if prefix else '', type(exc).__name__, ' in {!r}'.format(context) if context else ''
        ),
        Style.RESET_ALL,
        sep='',
        file=sys.stderr,
    )
    print(trace)
