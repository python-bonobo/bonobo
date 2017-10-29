import io
import sys
from contextlib import redirect_stdout

from colorama import Style, Fore, init

init(wrap=True)

from bonobo import settings
from bonobo.plugins import Plugin
from bonobo.util.term import CLEAR_EOL, MOVE_CURSOR_UP


class IOBuffer():
    """
    The role of IOBuffer is to overcome the problem of multiple threads wanting to write to stdout at the same time. It
    works a bit like a videogame: there are two buffers, one that is used to write, and one which is used to read from.
    On each cycle, we swap the buffers, and the console plugin handle output of the one which is not anymore "active".

    """

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

    def flush(self):
        self.current.flush()


class ConsoleOutputPlugin(Plugin):
    """
    Outputs status information to the connected stdout. Can be a TTY, with or without support for colors/cursor
    movements, or a non tty (pipe, file, ...). The features are adapted to terminal capabilities.

    On Windows, we'll play a bit differently because we don't know how to manipulate cursor position. We'll only
    display stats at the very end, and there won't be this "buffering" logic we need to display both stats and stdout.

    .. attribute:: prefix

        String prefix of output lines.

    """

    def __init__(self, context):
        super(ConsoleOutputPlugin, self).__init__(context)
        self._reset()

    def _reset(self):
        self.prefix = ''
        self.counter = 0
        self._append_cache = ''
        self.isatty = sys.stdout.isatty()
        self.iswindows = (sys.platform == 'win32')

    def initialize(self):
        self._reset()
        self._stdout = sys.stdout
        self.stdout = IOBuffer()
        self.redirect_stdout = redirect_stdout(self._stdout if self.iswindows else self.stdout)
        self.redirect_stdout.__enter__()

    def run(self):
        if self.isatty and not self.iswindows:
            self._write(self.context.parent, rewind=True)
        else:
            pass  # not a tty, or windows, so we'll ignore stats output

    def finalize(self):
        self._write(self.context.parent, rewind=False)
        self.redirect_stdout.__exit__(None, None, None)

    def write(self, context, prefix='', rewind=True, append=None):
        t_cnt = len(context)

        if not self.iswindows:
            buffered = self.stdout.switch()
            for line in buffered.split('\n')[:-1]:
                print(line + CLEAR_EOL, file=sys.stderr)

        alive_color = Style.BRIGHT
        dead_color = Style.BRIGHT + Fore.BLACK

        for i in context.graph.topologically_sorted_indexes:
            node = context[i]
            name_suffix = '({})'.format(i) if settings.DEBUG.get() else ''
            if node.alive:
                _line = ''.join(
                    (
                        ' ',
                        alive_color,
                        '+',
                        Style.RESET_ALL,
                        ' ',
                        node.name,
                        name_suffix,
                        ' ',
                        node.get_statistics_as_string(),
                        Style.RESET_ALL,
                        ' ',
                    )
                )
            else:
                _line = ''.join(
                    (
                        ' ',
                        dead_color,
                        '-',
                        ' ',
                        node.name,
                        name_suffix,
                        ' ',
                        node.get_statistics_as_string(),
                        Style.RESET_ALL,
                        ' ',
                    )
                )
            print(prefix + _line + '\033[0K', file=sys.stderr)

        if append:
            # todo handle multiline
            print(
                ''.join(
                    (
                        ' `-> ', ' '.join('{}{}{}: {}'.format(Style.BRIGHT, k, Style.RESET_ALL, v) for k, v in append),
                        CLEAR_EOL
                    )
                ),
                file=sys.stderr
            )
            t_cnt += 1

        if rewind:
            print(CLEAR_EOL, file=sys.stderr)
            print(MOVE_CURSOR_UP(t_cnt + 2), file=sys.stderr)

    def _write(self, graph_context, rewind):
        if settings.PROFILE.get():
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
