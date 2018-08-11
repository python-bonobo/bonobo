import contextlib
import functools
import io
import os
import runpy
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from unittest.mock import patch

import pytest

from bonobo import __main__, get_examples_path, open_fs
from bonobo.commands import entrypoint
from bonobo.constants import Token
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
    def __init__(self, extension='txt', mode='w', *, input_data=''):
        self.extension = extension
        self.input_data = input_data
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
        return [row._asdict() if hasattr(row, '_asdict') else dict(row) for row in self.buffer]


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
    'target', [(get_examples_path('environ.py'),), ('-m', 'bonobo.examples.environ')]
)


@all_runners
@all_environ_targets
class EnvironmentTestCase:
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


class StaticNodeTest:
    node = None
    services = {}

    NodeExecutionContextType = BufferingNodeExecutionContext

    @contextlib.contextmanager
    def execute(self, *args, **kwargs):
        with self.NodeExecutionContextType(type(self).node, services=self.services) as context:
            yield context

    def call(self, *args, **kwargs):
        return type(self).node(*args, **kwargs)


class ConfigurableNodeTest:
    NodeType = None
    NodeExecutionContextType = BufferingNodeExecutionContext

    services = {}

    @staticmethod
    def incontext(*create_args, **create_kwargs):
        def decorator(method):
            @functools.wraps(method)
            def _incontext(self, *args, **kwargs):
                nonlocal create_args, create_kwargs
                with self.execute(*create_args, **create_kwargs) as context:
                    return method(self, context, *args, **kwargs)

            return _incontext

        return decorator

    def create(self, *args, **kwargs):
        return self.NodeType(*self.get_create_args(*args), **self.get_create_kwargs(**kwargs))

    @contextlib.contextmanager
    def execute(self, *args, **kwargs):
        with self.NodeExecutionContextType(self.create(*args, **kwargs), services=self.services) as context:
            yield context

    def get_create_args(self, *args):
        return args

    def get_create_kwargs(self, **kwargs):
        return kwargs

    def get_filesystem_tester(self):
        return FilesystemTester(self.extension, input_data=self.input_data)


class ReaderTest(ConfigurableNodeTest):
    """ Helper class to test reader transformations. """

    ReaderNodeType = None

    extension = 'txt'
    input_data = ''

    @property
    def NodeType(self):
        return self.ReaderNodeType

    @pytest.fixture(autouse=True)
    def _reader_test_fixture(self, tmpdir):
        fs_tester = self.get_filesystem_tester()
        self.fs, self.filename, self.services = fs_tester.get_services_for_reader(tmpdir)
        self.tmpdir = tmpdir

    def get_create_args(self, *args):
        return (self.filename,) + args

    def test_customizable_output_type_transform_not_a_type(self):
        context = self.NodeExecutionContextType(
            self.create(*self.get_create_args(), output_type=str.upper, **self.get_create_kwargs()),
            services=self.services,
        )
        with pytest.raises(TypeError):
            context.start()

    def test_customizable_output_type_transform_not_a_tuple(self):
        context = self.NodeExecutionContextType(
            self.create(
                *self.get_create_args(), output_type=type('UpperString', (str,), {}), **self.get_create_kwargs()
            ),
            services=self.services,
        )
        with pytest.raises(TypeError):
            context.start()


class WriterTest(ConfigurableNodeTest):
    """ Helper class to test writer transformations. """

    WriterNodeType = None

    extension = 'txt'
    input_data = ''

    @property
    def NodeType(self):
        return self.WriterNodeType

    @pytest.fixture(autouse=True)
    def _writer_test_fixture(self, tmpdir):
        fs_tester = self.get_filesystem_tester()
        self.fs, self.filename, self.services = fs_tester.get_services_for_writer(tmpdir)
        self.tmpdir = tmpdir

    def get_create_args(self, *args):
        return (self.filename,) + args

    def readlines(self):
        with self.fs.open(self.filename) as fp:
            return tuple(map(str.strip, fp.readlines()))
