import sys
from .core import Graph, NaiveStrategy, ProcessPoolExecutorStrategy, ThreadPoolExecutorStrategy, inject, service

PY35 = (sys.version_info >= (3, 5))

assert PY35, 'Python 3.5+ is required to use Bonobo.'

__all__ = [
    Graph,
    NaiveStrategy,
    ProcessPoolExecutorStrategy,
    ThreadPoolExecutorStrategy,
    inject,
    service,
]
