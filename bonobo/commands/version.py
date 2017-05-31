def format_version(mod, *, name=None, quiet=False):
    from bonobo.util.pkgs import bonobo_packages
    args = {
        'name': name or mod.__name__,
        'version': mod.__version__,
        'location': bonobo_packages[name or mod.__name__].location
    }

    if not quiet:
        return '{name} v.{version} (in {location})'.format(**args)
    if quiet < 2:
        return '{name} {version}'.format(**args)
    if quiet < 3:
        return '{version}'.format(**args)

    raise RuntimeError('Hard to be so quiet...')


def execute(all=False, quiet=False):
    import bonobo
    from bonobo.util.pkgs import bonobo_packages

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
    parser.add_argument('--quiet', '-q', action='count')
    return execute
