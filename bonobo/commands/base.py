import argparse
import logging
import runpy
import sys
from contextlib import contextmanager

import bonobo.util.environ
from bonobo.util import get_name
from bonobo.util.environ import get_argument_parser, parse_args


class BaseCommand:
    """
    Base class for CLI commands.

    """

    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = logging.getLogger(get_name(self))
            return self._logger

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this method.
        """
        raise NotImplementedError('Subclasses of BaseCommand must provide a handle() method')


class BaseGraphCommand(BaseCommand):
    """
    Base class for CLI commands that depends on a graph definition, either from a file or from a module.

    """

    required = True
    handler = None

    def add_arguments(self, parser):
        # target arguments (cannot provide both).
        source_group = parser.add_mutually_exclusive_group(required=self.required)
        source_group.add_argument('file', nargs='?', type=str)
        source_group.add_argument('-m', dest='mod', type=str)

        # add arguments to enforce system environment.
        parser = get_argument_parser(parser)

        return parser

    def parse_options(self, **options):
        return options

    def handle(self, file, mod, **options):
        options = self.parse_options(**options)
        with self.read(file, mod, **options) as (graph, graph_execution_options, options):
            return self.do_handle(graph, **graph_execution_options, **options)

    def do_handle(self, graph, **options):
        if not self.handler:
            raise RuntimeError('{} has no handler defined.'.format(get_name(self)))
        return self.handler(graph, **options)

    @contextmanager
    def read(self, file, mod, **options):
        _graph, _graph_execution_options = None, None

        def _record(graph, **graph_execution_options):
            nonlocal _graph, _graph_execution_options
            _graph, _graph_execution_options = graph, graph_execution_options

        with _override_runner(_record), parse_args(options) as options:
            _argv = sys.argv
            try:
                if file:
                    sys.argv = [file]
                    self._run_path(file)
                elif mod:
                    sys.argv = [mod]
                    self._run_module(mod)
                else:
                    raise RuntimeError('No target provided.')
            finally:
                sys.argv = _argv

            if _graph is None:
                raise RuntimeError('Could not find graph.')

            yield _graph, _graph_execution_options, options

    def _run_path(self, file):
        return runpy.run_path(file, run_name='__main__')

    def _run_module(self, mod):
        return runpy.run_module(mod, run_name='__main__')


@contextmanager
def _override_runner(runner):
    """
    Context manager that monkey patches `bonobo.run` function with our current command logic.

    :param runner: the callable that will handle the `run()` logic.
    """
    import bonobo

    _get_argument_parser = bonobo.util.environ.get_argument_parser
    _run = bonobo.run
    try:
        # Original get_argument_parser would create or update an argument parser with environment options, but here we
        # already had them parsed so let's patch with something that creates an empty one instead.
        def get_argument_parser(parser=None):
            return parser or argparse.ArgumentParser()

        bonobo.util.environ.get_argument_parser = get_argument_parser
        bonobo.run = runner

        yield runner
    finally:
        # Restore our saved values.
        bonobo.util.environ.get_argument_parser = _get_argument_parser
        bonobo.run = _run
