from logging import getLogger

from colorama import Fore, Back, Style
from django.core.management.base import BaseCommand, OutputWrapper

import bonobo
import bonobo.util
from bonobo.commands.run import get_default_services
from bonobo.ext.console import ConsoleOutputPlugin
from bonobo.util.term import CLEAR_EOL


class ETLCommand(BaseCommand):
    GraphType = bonobo.Graph

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
        return get_default_services(type(self).__file__)

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

        result = bonobo.run(
            self.get_graph(*args, **options),
            services=self.get_services(),
        )
        self.stdout = _stdout_backup

        return '\nReturn Value: ' + str(result)
