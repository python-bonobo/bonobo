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

from queue import Empty

import pytest

from bonobo.constants import BEGIN, END
from bonobo.errors import InactiveReadableError, InactiveWritableError
from bonobo.structs.inputs import Input


def test_input_runlevels():
    q = Input()

    # Before BEGIN, noone should be able to write in an Input queue.
    assert not q.alive
    with pytest.raises(InactiveWritableError):
        q.put("hello, unborn queue.")

    # Begin
    q.put(BEGIN)
    assert q.alive and q._runlevel == 1
    q.put("foo")

    # Second Begin
    q.put(BEGIN)
    assert q.alive and q._runlevel == 2
    q.put("bar")
    q.put(END)

    # FIFO
    assert q.get() == "foo"
    assert q.get() == "bar"

    # self.assertEqual(q.alive, False) XXX queue don't know it's dead yet, but it is ...
    # Async get raises Empty (End is not returned)
    with pytest.raises(Empty):
        q.get(block=False)
    assert q.alive

    # Before killing, let's slide some data in.
    q.put("baz")

    # Now kill the queue...
    q.put(END)
    with pytest.raises(InactiveWritableError):
        q.put("foo")

    # Still can get remaining data
    assert q.get() == "baz"
    with pytest.raises(InactiveReadableError):
        q.get()
