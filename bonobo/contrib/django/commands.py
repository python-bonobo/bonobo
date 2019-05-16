from logging import getLogger
from types import GeneratorType

from colorama import Back, Fore, Style
from mondrian import term

import bonobo
from bonobo.plugins.console import ConsoleOutputPlugin
from bonobo.util.term import CLEAR_EOL
from django.core.management import BaseCommand
from django.core.management.base import OutputWrapper

from .utils import create_or_update


class ETLCommand(BaseCommand):
    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = getLogger(type(self).__module__)
            return self._logger

    create_or_update = staticmethod(create_or_update)

    def create_parser(self, prog_name, subcommand):
        return bonobo.get_argument_parser(super().create_parser(prog_name, subcommand))

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def get_graph(self, *args, **options):
        def not_implemented():
            raise NotImplementedError('You must implement {}.get_graph() method.'.format(self))

        return bonobo.Graph(not_implemented)

    def get_services(self):
        return {}

    def get_strategy(self):
        return None

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def run(self, *args, **options):
        results = []
        with bonobo.parse_args(options) as options:
            services = self.get_services()
            strategy = self.get_strategy()
            graph_coll = self.get_graph(*args, **options)

            if not isinstance(graph_coll, GeneratorType):
                graph_coll = (graph_coll,)

            for i, graph in enumerate(graph_coll):
                if not isinstance(graph, bonobo.Graph):
                    raise ValueError('Expected a Graph instance, got {!r}.'.format(graph))
                print(term.lightwhite('{}. {}'.format(i + 1, graph.name)))
                result = bonobo.run(graph, services=services, strategy=strategy)
                results.append(result)
                print(term.lightblack(' ... return value: ' + str(result)))
                print()

        return results

    def handle(self, *args, **options):
        _stdout_backup, _stderr_backup = self.stdout, self.stderr

        self.stdout = OutputWrapper(ConsoleOutputPlugin._stdout, ending=CLEAR_EOL + '\n')
        self.stderr = OutputWrapper(ConsoleOutputPlugin._stderr, ending=CLEAR_EOL + '\n')
        self.stderr.style_func = lambda x: Fore.LIGHTRED_EX + Back.RED + '!' + Style.RESET_ALL + ' ' + x

        self.run(*args, **options)

        self.stdout, self.stderr = _stdout_backup, _stderr_backup
