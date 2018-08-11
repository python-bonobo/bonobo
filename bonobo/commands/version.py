from bonobo.commands import BaseCommand


def get_versions(*, all=False, quiet=None):
    import bonobo
    from bonobo.util.pkgs import bonobo_packages

    yield _format_version(bonobo, quiet=quiet)

    if all:
        for name in sorted(bonobo_packages):
            if name != 'bonobo':
                try:
                    mod = __import__(name.replace('-', '_'))
                    try:
                        yield _format_version(mod, name=name, quiet=quiet)
                    except Exception as exc:
                        yield '{} ({})'.format(name, exc)
                except ImportError as exc:
                    yield '{} is not importable ({}).'.format(name, exc)


class VersionCommand(BaseCommand):
    def handle(self, *, all=False, quiet=False):
        for line in get_versions(all=all, quiet=quiet):
            print(line)

    def add_arguments(self, parser):
        parser.add_argument('--all', '-a', action='store_true')
        parser.add_argument('--quiet', '-q', action='count')


def _format_version(mod, *, name=None, quiet=False):
    from bonobo.util.pkgs import bonobo_packages

    args = {
        'name': name or mod.__name__,
        'version': mod.__version__,
        'location': bonobo_packages[name or mod.__name__].location,
    }

    if not quiet:
        return '{name} v.{version} (in {location})'.format(**args)
    if quiet < 2:
        return '{name} {version}'.format(**args)
    if quiet < 3:
        return '{version}'.format(**args)

    raise RuntimeError('Hard to be so quiet...')
