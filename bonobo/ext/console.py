import io
import sys
from contextlib import redirect_stdout

from colorama import Style, Fore

from bonobo import settings
from bonobo.plugins import Plugin
from bonobo.util.term import CLEAR_EOL, MOVE_CURSOR_UP


class IOBuffer():
    def __init__(self):
        self.current = io.StringIO()
        self.write = self.current.write

    def switch(self):
        previous = self.current
        self.current = io.StringIO()
        self.write = self.current.write
        try:
            return previous.getvalue()
        finally:
            previous.close()


class ConsoleOutputPlugin(Plugin):
    """
    Outputs status information to the connected stdout. Can be a TTY, with or without support for colors/cursor
    movements, or a non tty (pipe, file, ...). The features are adapted to terminal capabilities.

    .. attribute:: prefix

        String prefix of output lines.

    """

    def initialize(self):
        self.prefix = ''
        self.counter = 0
        self._append_cache = ''
        self.isatty = sys.stdout.isatty()

        self._stdout = sys.stdout
        self.stdout = IOBuffer()
        self.redirect_stdout = redirect_stdout(self.stdout)
        self.redirect_stdout.__enter__()

    def run(self):
        if self.isatty:
            self._write(self.context.parent, rewind=True)
        else:
            pass  # not a tty

    def finalize(self):
        self._write(self.context.parent, rewind=False)
        self.redirect_stdout.__exit__(None, None, None)

    def write(self, context, prefix='', rewind=True, append=None):
        t_cnt = len(context)

        buffered = self.stdout.switch()
        for line in buffered.split('\n')[:-1]:
            print(line + CLEAR_EOL, file=sys.stderr)

        for i in context.graph.topologically_sorted_indexes:
            node = context[i]
            name_suffix = '({})'.format(i) if settings.DEBUG else ''
            if node.alive:
                _line = ''.join(
                    (
                        ' ', Style.BRIGHT, '+', Style.RESET_ALL, ' ', node.name, name_suffix, ' ',
                        node.get_statistics_as_string(), Style.RESET_ALL, ' ',
                    )
                )
            else:
                _line = ''.join(
                    (
                        ' ', Fore.BLACK, '-', ' ', node.name, name_suffix, ' ', node.get_statistics_as_string(),
                        Style.RESET_ALL, ' ',
                    )
                )
            print(prefix + _line + '\033[0K', file=sys.stderr)

        if append:
            # todo handle multiline
            print(
                ''.join(
                    (
                        ' `-> ', ' '.join('{}{}{}: {}'.format(Style.BRIGHT, k, Style.RESET_ALL, v)
                                          for k, v in append), CLEAR_EOL
                    )
                ),
                file=sys.stderr
            )
            t_cnt += 1

        if rewind:
            print(CLEAR_EOL, file=sys.stderr)
            print(MOVE_CURSOR_UP(t_cnt + 2), file=sys.stderr)

    def _write(self, graph_context, rewind):
        if settings.PROFILE:
            if self.counter % 10 and self._append_cache:
                append = self._append_cache
            else:
                self._append_cache = append = (
                    ('Memory', '{0:.2f} Mb'.format(memory_usage())),
                    # ('Total time', '{0} s'.format(execution_time(harness))),
                )
        else:
            append = ()
        self.write(graph_context, prefix=self.prefix, append=append, rewind=rewind)
        self.counter += 1


def memory_usage():
    import os, psutil
    process = psutil.Process(os.getpid())
    return process.memory_info()[0] / float(2**20)
