"""
.. data:: START

    Event dispatched before execution starts.

.. data:: STARTED

    Event dispatched after execution starts.

.. data:: TICK

    Event dispatched while execution runs, on a regular basis (on each "tick").

.. data:: STOP

    Event dispatched before execution stops.

.. data:: STOPPED

    Event dispatched after execution stops.

.. data:: KILL

    Event dispatched when execution is killed.

"""

from whistle import Event

START = 'execution.start'
STARTED = 'execution.started'
TICK = 'execution.tick'
STOP = 'execution.stop'
STOPPED = 'execution.stopped'
KILL = 'execution.kill'


class ExecutionEvent(Event):
    def __init__(self, context):
        self.context = context
