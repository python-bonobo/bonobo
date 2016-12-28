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

import os
from functools import lru_cache
import blessings

import psutil

from bonobo.core.plugins import Plugin

t = blessings.Terminal()


@lru_cache(1)
def memory_usage():
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

    def __init__(self, prefix=''):
        self.prefix = prefix

    def _write(self, context, rewind):
        profile, debug = False, False
        if profile:
            append = (('Memory', '{0:.2f} Mb'.format(memory_usage())),
                      # ('Total time', '{0} s'.format(execution_time(harness))),
                      )
        else:
            append = ()
        self.write(context, prefix=self.prefix, append=append, debug=debug, profile=profile, rewind=rewind)

        # self.widget.value = [repr(component) for component in context.parent.components]

    def run(self, context):
        if t.is_a_tty:
            self._write(context.parent, rewind=True)
        else:
            pass  # not a tty

    def finalize(self, context):
        self._write(context.parent, rewind=False)

    @staticmethod
    def write(context, prefix='', rewind=True, append=None, debug=False, profile=False):
        t_cnt = len(context)

        for i, component in enumerate(context):
            if component.alive:
                _line = ''.join((
                    t.black('({})'.format(i + 1)),
                    ' ',
                    t.bold(t.white('+')),
                    ' ',
                    component.name,
                    ' ',
                    component.get_stats_as_string(
                        debug=debug, profile=profile),
                    ' ', ))
            else:
                _line = t.black(''.join((
                    '({})'.format(i + 1),
                    ' - ',
                    component.name,
                    ' ',
                    component.get_stats_as_string(
                        debug=debug, profile=profile),
                    ' ', )))
            print(prefix + _line + t.clear_eol)

        if append:
            # todo handle multiline
            print(' `->', ' '.join('{0}: {1}'.format(t.bold(t.white(k)), v) for k, v in append), t.clear_eol)
            t_cnt += 1

        if rewind:
            print(t.clear_eol)
            print(t.move_up * (t_cnt + 2))
