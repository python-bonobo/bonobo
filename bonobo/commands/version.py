import bonobo
from bonobo.util.pkgs import bonobo_packages


def format_version(mod, *, name=None, quiet=False):
    return ('{name} {version}' if quiet else '{name} v.{version} (in {location})').format(
        name=name or mod.__name__,
        version=mod.__version__,
        location=bonobo_packages[name or mod.__name__].location
    )


def execute(all=False, quiet=False):
    print(format_version(bonobo, quiet=quiet))
    if all:
        for name in sorted(bonobo_packages):
            if name != 'bonobo':
                try:
                    mod = __import__(name.replace('-', '_'))
                    try:
                        print(format_version(mod, name=name, quiet=quiet))
                    except Exception as exc:
                        print('{} ({})'.format(name, exc))
                except ImportError as exc:
                    print('{} is not importable ({}).'.format(name, exc))


def register(parser):
    parser.add_argument('--all', '-a', action='store_true')
    parser.add_argument('--quiet', '-q', action='store_true')
    return execute
