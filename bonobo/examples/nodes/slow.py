import bonobo
import time

from bonobo.constants import NOT_MODIFIED


def pause(*args, **kwargs):
    time.sleep(0.1)
    return NOT_MODIFIED


graph = bonobo.Graph(
    lambda: tuple(range(20)),
    pause,
    print,
)
