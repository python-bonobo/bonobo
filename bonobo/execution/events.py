from whistle import Event

START = 'execution.start'
STARTED = 'execution.started'
TICK = 'execution.tick'
STOP = 'execution.stop'
STOPPED = 'execution.stopped'
KILL = 'execution.kill'


class ExecutionEvent(Event):
    def __init__(self, graph_context):
        self.graph_context = graph_context
