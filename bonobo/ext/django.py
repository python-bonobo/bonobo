from logging import getLogger

import bonobo
import bonobo.util
from bonobo.plugins.console import ConsoleOutputPlugin
from bonobo.util.term import CLEAR_EOL
from colorama import Fore, Back, Style
from django.core.management.base import BaseCommand, OutputWrapper


class ETLCommand(BaseCommand):
    GraphType = bonobo.Graph

    def create_parser(self, prog_name, subcommand):
        return bonobo.get_argument_parser(
            super().create_parser(prog_name, subcommand)
        )

    def create_or_update(self, model, *, defaults=None, save=True, **kwargs):
        """
        Create or update a django model instance.

        :param model:
        :param defaults:
        :param kwargs:
        :return: object, created, updated

        """
        obj, created = model._default_manager.get_or_create(defaults=defaults, **kwargs)

        updated = False
        if not created:
            for k, v in defaults.items():
                if getattr(obj, k) != v:
                    setattr(obj, k, v)
                    updated = True

            if updated and save:
                obj.save()

        return obj, created, updated

    def get_graph(self, *args, **options):
        def not_implemented():
            raise NotImplementedError('You must implement {}.get_graph() method.'.format(self))

        return self.GraphType(not_implemented)

    def get_services(self):
        return {}

    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = getLogger(type(self).__module__)
            return self._logger

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def handle(self, *args, **options):
        _stdout_backup, _stderr_backup = self.stdout, self.stderr

        self.stdout = OutputWrapper(ConsoleOutputPlugin._stdout, ending=CLEAR_EOL + '\n')
        self.stderr = OutputWrapper(ConsoleOutputPlugin._stderr, ending=CLEAR_EOL + '\n')
        self.stderr.style_func = lambda x: Fore.LIGHTRED_EX + Back.RED + '!' + Style.RESET_ALL + ' ' + x

        with bonobo.parse_args(options) as options:
            result = bonobo.run(
                self.get_graph(*args, **options),
                services=self.get_services(),
            )

        self.stdout, self.stderr = _stdout_backup, _stderr_backup

        return '\nReturn Value: ' + str(result)
