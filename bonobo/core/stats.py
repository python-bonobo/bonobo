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

from abc import ABCMeta, abstractmethod

from bonobo.core.errors import AbstractError


class WithStatistics(metaclass=ABCMeta):
    @abstractmethod
    def get_stats(self, *args, **kwargs):
        raise AbstractError(self.get_stats)

    def get_stats_as_string(self, *args, **kwargs):
        return ' '.join(('{0}={1}'.format(name, cnt) for name, cnt in self.get_stats(*args, **kwargs) if cnt > 0))
