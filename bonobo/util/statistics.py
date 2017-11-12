# -*- coding: utf-8 -*-
#
# copyright 2012-2014 romain dorgueil
#
# licensed under the apache license, version 2.0 (the "license");
# you may not use this file except in compliance with the license.
# you may obtain a copy of the license at
#
#     http://www.apache.org/licenses/license-2.0
#
# unless required by applicable law or agreed to in writing, software
# distributed under the license is distributed on an "as is" basis,
# without warranties or conditions of any kind, either express or implied.
# see the license for the specific language governing permissions and
# limitations under the license.
import time


class WithStatistics:
    def __init__(self, *names):
        self.statistics_names = names
        self.statistics = {name: 0 for name in names}

    def get_statistics(self, *args, **kwargs):
        return ((name, self.statistics[name]) for name in self.statistics_names)

    def get_statistics_as_string(self, *args, **kwargs):
        stats = tuple('{0}={1}'.format(name, cnt) for name, cnt in self.get_statistics(*args, **kwargs) if cnt > 0)
        return (kwargs.get('prefix', '') + ' '.join(stats)) if len(stats) else ''

    def increment(self, name, *, amount=1):
        self.statistics[name] += amount


class Timer:
    """
    Context manager used to time execution of stuff.
    """

    def __enter__(self):
        self.__start = time.time()

    def __exit__(self, type=None, value=None, traceback=None):
        # Error handling here
        self.__finish = time.time()

    @property
    def duration(self):
        return self.__finish - self.__start

    def __str__(self):
        return str(int(self.duration * 1000) / 1000.0) + 's'
