import functools
import io
import os
import runpy
import sys
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from unittest.mock import patch

import pytest

from bonobo import open_fs, Token, __main__, get_examples_path, Bag
from bonobo.commands import entrypoint
from bonobo.execution.contexts.graph import GraphExecutionContext
from bonobo.execution.contexts.node import NodeExecutionContext


@contextmanager
def optional_contextmanager(cm, *, ignore=False):
    if cm is None or ignore:
        yield
    else:
        with cm:
            yield


class FilesystemTester:
    def __init__(self, extension='txt', mode='w'):
        self.extension = extension
        self.input_data = ''
        self.mode = mode

    def get_services_for_reader(self, tmpdir):
        fs, filename = open_fs(tmpdir), 'input.' + self.extension
        with fs.open(filename, self.mode) as fp:
            fp.write(self.input_data)
        return fs, filename, {'fs': fs}

    def get_services_for_writer(self, tmpdir):
        fs, filename = open_fs(tmpdir), 'output.' + self.extension
        return fs, filename, {'fs': fs}


class QueueList(list):
    def append(self, item):
        if not isinstance(item, Token):
            super(QueueList, self).append(item)

    put = append


class BufferingContext:
    def __init__(self, buffer=None):
        if buffer is None:
            buffer = QueueList()
        self.buffer = buffer

    def get_buffer(self):
        return self.buffer

    def get_buffer_args_as_dicts(self):
        return list(map(lambda x: x.args_as_dict() if isinstance(x, Bag) else dict(x), self.buffer))


class BufferingNodeExecutionContext(BufferingContext, NodeExecutionContext):
    def __init__(self, *args, buffer=None, **kwargs):
        BufferingContext.__init__(self, buffer)
        NodeExecutionContext.__init__(self, *args, **kwargs, _outputs=[self.buffer])


class BufferingGraphExecutionContext(BufferingContext, GraphExecutionContext):
    NodeExecutionContextType = BufferingNodeExecutionContext

    def __init__(self, *args, buffer=None, **kwargs):
        BufferingContext.__init__(self, buffer)
        GraphExecutionContext.__init__(self, *args, **kwargs)

    def create_node_execution_context_for(self, node):
        return self.NodeExecutionContextType(node, parent=self, buffer=self.buffer)


def runner(f):
    @functools.wraps(f)
    def wrapped_runner(*args, catch_errors=False):
        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
            try:
                f(list(args))
            except BaseException as exc:
                if not catch_errors:
                    raise
                elif isinstance(catch_errors, BaseException) and not isinstance(exc, catch_errors):
                    raise
                return stdout.getvalue(), stderr.getvalue(), exc
        return stdout.getvalue(), stderr.getvalue()

    return wrapped_runner


@runner
def runner_entrypoint(args):
    """ Run bonobo using the python command entrypoint directly (bonobo.commands.entrypoint). """
    return entrypoint(args)


@runner
def runner_module(args):
    """ Run bonobo using the bonobo.__main__ file, which is equivalent as doing "python -m bonobo ..."."""
    with patch.object(sys, 'argv', ['bonobo', *args]):
        return runpy.run_path(__main__.__file__, run_name='__main__')


all_runners = pytest.mark.parametrize('runner', [runner_entrypoint, runner_module])
all_environ_targets = pytest.mark.parametrize(
    'target', [
        (get_examples_path('environ.py'), ),
        (
            '-m',
            'bonobo.examples.environ',
        ),
    ]
)


@all_runners
@all_environ_targets
class EnvironmentTestCase():
    def run_quiet(self, runner, *args):
        return runner('run', '--quiet', *args)

    def run_environ(self, runner, *args, environ=None):
        _environ = {'PATH': '/usr/bin'}
        if environ:
            _environ.update(environ)

        with patch.dict('os.environ', _environ, clear=True):
            out, err = self.run_quiet(runner, *args)
            assert 'SECRET' not in os.environ
            assert 'PASSWORD' not in os.environ
            if 'PATH' in _environ:
                assert 'PATH' in os.environ
                assert os.environ['PATH'] == _environ['PATH']

        assert err == ''
        return dict(map(lambda line: line.split(' ', 1), filter(None, out.split('\n'))))
