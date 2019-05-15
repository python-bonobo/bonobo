import logging
import re
from contextlib import contextmanager
from sys import exc_info

from mondrian import term

logger = logging.getLogger(__name__)


@contextmanager
def sweeten_errors():
    try:
        yield
    except Exception as exc:
        SPACES = 2
        w = term.white
        prefix = w("║" + " " * (SPACES - 1))
        suffix = w(" " * (SPACES - 1) + "║")

        pre_re = re.compile("([^`]*)`([^`]*)`([^`]*)")

        def format_arg(arg):
            length = len(pre_re.sub("\\1\\2\\3", arg))

            arg = pre_re.sub(w("\\1") + term.bold("\\2") + w("\\3"), arg)
            arg = re.sub(r"^  \$ (.*)", term.lightblack("  $ ") + term.reset("\\1"), arg)

            return (arg, length)

        def f(*args):
            return "".join(args)

        term_width, term_height = term.get_size()
        line_length = min(80, term_width)
        for arg in exc.args:
            line_length = max(min(line_length, len(arg) + 2 * SPACES), 120)

        print(f(w("╔" + "═" * (line_length - 2) + "╗")))
        for i, arg in enumerate(exc.args):

            if i == 1:
                print(f(prefix, " " * (line_length - 2 * SPACES), suffix))

            arg_formatted, arg_length = format_arg(arg)
            if not i:
                # first line
                print(
                    f(
                        prefix,
                        term.red_bg(term.bold(" " + type(exc).__name__ + " ")),
                        " ",
                        w(arg_formatted),
                        " " * (line_length - (arg_length + 3 + len(type(exc).__name__) + 2 * SPACES)),
                        suffix,
                    )
                )
            else:
                # other lines
                print(f(prefix, arg_formatted + " " * (line_length - arg_length - 2 * SPACES), suffix))

        print(f(w("╚" + "═" * (line_length - 2) + "╝")))

        logging.getLogger().debug("This error was caused by the following exception chain.", exc_info=exc_info())
