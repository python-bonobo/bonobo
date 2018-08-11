import os

import bonobo
from bonobo.commands import BaseGraphCommand


class RunCommand(BaseGraphCommand):
    install = False
    handler = staticmethod(bonobo.run)

    def add_arguments(self, parser):
        super(RunCommand, self).add_arguments(parser)

        verbosity_group = parser.add_mutually_exclusive_group()
        verbosity_group.add_argument('--quiet', '-q', action='store_true')
        verbosity_group.add_argument('--verbose', '-v', action='store_true')

        parser.add_argument('--install', '-I', action='store_true')

    def parse_options(self, *, quiet=False, verbose=False, install=False, **options):
        from bonobo import settings

        settings.QUIET.set_if_true(quiet)
        settings.DEBUG.set_if_true(verbose)
        self.install = install
        return options

    def _run_path(self, file):
        # add install logic
        if self.install:
            if os.path.isdir(file):
                requirements = os.path.join(file, 'requirements.txt')
            else:
                requirements = os.path.join(os.path.dirname(file), 'requirements.txt')
            _install_requirements(requirements)

        return super()._run_path(file)

    def _run_module(self, mod):
        # install not implemented for a module, not sure it even make sense.
        if self.install:
            raise RuntimeError('--install behaviour when running a module is not defined.')

        return super()._run_module(mod)


def register_generic_run_arguments(parser, required=True):
    """
    Only there for backward compatibility with third party extensions.
    TODO: This should be deprecated (using the @deprecated decorator) in 0.7, and removed in 0.8 or 0.9.
    """
    dummy_command = BaseGraphCommand()
    dummy_command.required = required
    dummy_command.add_arguments(parser)
    return parser


def _install_requirements(requirements):
    """Install requirements given a path to requirements.txt file."""
    import importlib
    import pip

    pip.main(['install', '-r', requirements])
    # Some shenanigans to be sure everything is importable after this, especially .egg-link files which
    # are referenced in *.pth files and apparently loaded by site.py at some magic bootstrap moment of the
    # python interpreter.
    pip.utils.pkg_resources = importlib.reload(pip.utils.pkg_resources)
    import site

    importlib.reload(site)
