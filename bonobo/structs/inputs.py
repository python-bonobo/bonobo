# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 Romain Dorgueil
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

from abc import ABCMeta, abstractmethod
from queue import Queue

from bonobo.constants import BEGIN, END
from bonobo.errors import AbstractError, InactiveReadableError, InactiveWritableError

BUFFER_SIZE = 8192


class Readable(metaclass=ABCMeta):
    """Interface for things you can read from."""

    @abstractmethod
    def get(self, block=True, timeout=None):
        """Read. Block/timeout are there for Queue compat."""
        raise AbstractError(self.get)


class Writable(metaclass=ABCMeta):
    """Interface for things you can write to."""

    @abstractmethod
    def put(self, data, block=True, timeout=None):
        """Write. Block/timeout are there for Queue compat."""
        raise AbstractError(self.put)


class Input(Queue, Readable, Writable):
    def __init__(self, maxsize=BUFFER_SIZE, *, daemon=False):
        Queue.__init__(self, maxsize)

        self._daemon = bool(daemon)
        self._runlevel = 0
        self._writable_runlevel = 0
        self.on_initialize = []
        self.on_begin = []
        self.on_end = []
        self.on_finalize = []

    def daemonize(self, daemon=True):
        self._daemon = bool(daemon)

    def call_event_handlers(self, handlers):
        for handler in handlers:
            handler()

    def put(self, data, block=True, timeout=None):
        # Begin token is a metadata to raise the input runlevel.
        if data == BEGIN:
            if not self._runlevel:
                self.call_event_handlers(self.on_initialize)

            self._runlevel += 1
            self._writable_runlevel += 1

            # callback
            self.call_event_handlers(self.on_begin)

            return

        # Check we are actually able to receive data.
        if self._writable_runlevel < 1 and not self._daemon:
            raise InactiveWritableError("Cannot put() on an inactive {}.".format(Writable.__name__))

        if data == END:
            self._writable_runlevel -= 1

        return Queue.put(self, data, block, timeout)

    def _decrement_runlevel(self):
        if self._runlevel == 1:
            self.call_event_handlers(self.on_finalize)
        self._runlevel -= 1
        self.call_event_handlers(self.on_end)

    def get(self, block=True, timeout=None):
        if not self.alive:
            raise InactiveReadableError("Cannot get() on an inactive {}.".format(Readable.__name__))

        data = Queue.get(self, block, timeout)

        if data == END:
            self._decrement_runlevel()

            if not self.alive:
                raise InactiveReadableError(
                    "Cannot get() on an inactive {} (runlevel just reached 0).".format(Readable.__name__)
                )
            return self.get(block, timeout)

        return data

    def shutdown(self):
        while self._runlevel >= 1:
            self._decrement_runlevel()

    def empty(self):
        self.mutex.acquire()
        while self._qsize() and self.queue[0] == END:
            self._runlevel -= 1
            Queue._get(self)
        self.mutex.release()

        return Queue.empty(self)

    @property
    def alive(self):
        return self._daemon or self._runlevel > 0


class Pipe(Input):
    def __init__(self, maxsize=0, **kwargs):
        super().__init__(maxsize=maxsize, **kwargs)
        self.targets = []

    def put(self, item, block=True, timeout=None):
        if len(self.targets):
            for target in self.targets:
                target.put(item, block=block, timeout=timeout)
        else:
            super().put(item, block=block, timeout=timeout)

    def __len__(self):
        return len(self.targets)

    def __bool__(self):
        return True
