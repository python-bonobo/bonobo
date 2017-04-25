# -*- coding: utf-8 -*-
#
# Copyright 2012-2017 Romain Dorgueil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import sys

from colorama import Fore, Style

from bonobo.plugins import Plugin
from bonobo.util.term import CLEAR_EOL, MOVE_CURSOR_UP


@functools.lru_cache(1)
def memory_usage():
    import os, psutil
    process = psutil.Process(os.getpid())
    return process.get_memory_info()[0] / float(2**20)


# @lru_cache(64)
# def execution_time(harness):
#    return datetime.datetime.now() - harness._started_at


class ConsoleOutputPlugin(Plugin):
    """
    Outputs status information to the connected stdout. Can be a TTY, with or without support for colors/cursor
    movements, or a non tty (pipe, file, ...). The features are adapted to terminal capabilities.

    .. attribute:: prefix

        String prefix of output lines.

    """

    def initialize(self):
        self.prefix = ''

    def _write(self, graph_context, rewind):
        profile, debug = False, False
        if profile:
            append = (
                ('Memory', '{0:.2f} Mb'.format(memory_usage())),
                # ('Total time', '{0} s'.format(execution_time(harness))),
            )
        else:
            append = ()
        self.write(graph_context, prefix=self.prefix, append=append, debug=debug, profile=profile, rewind=rewind)

    def run(self):
        if sys.stdout.isatty():
            self._write(self.context.parent, rewind=True)
        else:
            pass  # not a tty

    def finalize(self):
        self._write(self.context.parent, rewind=False)

    @staticmethod
    def write(context, prefix='', rewind=True, append=None, debug=False, profile=False):
        t_cnt = len(context)

        for i, component in enumerate(context):
            if component.alive:
                _line = ''.join(
                    (
                        Fore.BLACK, '({})'.format(i + 1), Style.RESET_ALL, ' ', Style.BRIGHT, '+', Style.RESET_ALL, ' ',
                        component.name, ' ', component.get_statistics_as_string(debug=debug,
                                                                                profile=profile), Style.RESET_ALL, ' ',
                    )
                )
            else:
                _line = ''.join(
                    (
                        Fore.BLACK, '({})'.format(i + 1), ' - ', component.name, ' ',
                        component.get_statistics_as_string(debug=debug, profile=profile), Style.RESET_ALL, ' ',
                    )
                )
            print(prefix + _line + '\033[0K')

        if append:
            # todo handle multiline
            print(
                ''.join(
                    (
                        ' `-> ', ' '.join('{}{}{}: {}'.format(Style.BRIGHT, k, Style.RESET_ALL, v)
                                          for k, v in append), CLEAR_EOL
                    )
                )
            )
            t_cnt += 1

        if rewind:
            print(CLEAR_EOL)
            print(MOVE_CURSOR_UP(t_cnt + 2))
