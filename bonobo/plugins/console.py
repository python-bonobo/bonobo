import io
import sys
from contextlib import redirect_stderr, redirect_stdout

from colorama import Fore, Style
from colorama import init as initialize_colorama_output_wrappers

from bonobo import settings
from bonobo.execution import events
from bonobo.plugins import Plugin
from bonobo.util.term import CLEAR_EOL, MOVE_CURSOR_UP

initialize_colorama_output_wrappers(wrap=True)


class ConsoleOutputPlugin(Plugin):
    """
    Outputs status information to the connected stdout. Can be a TTY, with or without support for colors/cursor
    movements, or a non tty (pipe, file, ...). The features are adapted to terminal capabilities.

    On Windows, we'll play a bit differently because we don't know how to manipulate cursor position. We'll only
    display stats at the very end, and there won't be this "buffering" logic we need to display both stats and stdout.

    .. attribute:: prefix

        String prefix of output lines.

    """

    # Standard outputs descriptors backup here, also used to override if needed.
    _stdout = sys.stdout
    _stderr = sys.stderr

    # When the plugin is instanciated, we'll set the real value of this.
    isatty = False

    # Whether we're on windows, or a real operating system.
    iswindows = sys.platform == 'win32'

    def __init__(self):
        self.isatty = self._stdout.isatty()

    def register(self, dispatcher):
        dispatcher.add_listener(events.START, self.setup)
        dispatcher.add_listener(events.TICK, self.tick)
        dispatcher.add_listener(events.STOPPED, self.teardown)

    def unregister(self, dispatcher):
        dispatcher.remove_listener(events.STOPPED, self.teardown)
        dispatcher.remove_listener(events.TICK, self.tick)
        dispatcher.remove_listener(events.START, self.setup)

    def setup(self, event):
        # TODO this wont work if one instance is registered with more than one context.
        # Two options:
        # - move state to context
        # - forbid registering more than once
        self.prefix = ''
        self.counter = 0
        self._append_cache = ''

        self.stdout = IOBuffer()
        self.redirect_stdout = redirect_stdout(self._stdout if self.iswindows else self.stdout)
        self.redirect_stdout.__enter__()

        self.stderr = IOBuffer()
        self.redirect_stderr = redirect_stderr(self._stderr if self.iswindows else self.stderr)
        self.redirect_stderr.__enter__()

    def tick(self, event):
        if self.isatty and not self.iswindows:
            self._write(event.context, rewind=True)
        else:
            pass  # not a tty, or windows, so we'll ignore stats output

    def teardown(self, event):
        self._write(event.context, rewind=False)
        self.redirect_stderr.__exit__(None, None, None)
        self.redirect_stdout.__exit__(None, None, None)

    def write(self, context, prefix='', rewind=True, append=None):
        t_cnt = len(context)

        if not self.iswindows:
            for line in self.stdout.switch().split('\n')[:-1]:
                print(line + CLEAR_EOL, file=self._stdout)
            for line in self.stderr.switch().split('\n')[:-1]:
                print(line + CLEAR_EOL, file=self._stderr)

        alive_color = Style.BRIGHT
        dead_color = Style.BRIGHT + Fore.BLACK

        for i in context.graph.topologically_sorted_indexes:
            node = context[i]
            name_suffix = '({})'.format(i) if settings.DEBUG.get() else ''

            liveliness_color = alive_color if node.alive else dead_color
            liveliness_prefix = ' {}{}{} '.format(liveliness_color, node.status, Style.RESET_ALL)
            _line = ''.join(
                (
                    liveliness_prefix,
                    node.name,
                    name_suffix,
                    ' ',
                    node.get_statistics_as_string(),
                    ' ',
                    node.get_flags_as_string(),
                    Style.RESET_ALL,
                    ' ',
                )
            )
            print(prefix + _line + CLEAR_EOL, file=self._stderr)

        if append:
            # todo handle multiline
            print(
                ''.join(
                    (
                        ' `-> ',
                        ' '.join('{}{}{}: {}'.format(Style.BRIGHT, k, Style.RESET_ALL, v) for k, v in append),
                        CLEAR_EOL,
                    )
                ),
                file=self._stderr,
            )
            t_cnt += 1

        if rewind:
            print(CLEAR_EOL, file=self._stderr)
            print(MOVE_CURSOR_UP(t_cnt + 2), file=self._stderr)

    def _write(self, context, rewind):
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
        self.write(context, prefix=self.prefix, append=append, rewind=rewind)
        self.counter += 1


class IOBuffer:
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


def memory_usage():
    import os, psutil

    process = psutil.Process(os.getpid())
    return process.memory_info()[0] / float(2 ** 20)
