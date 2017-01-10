import os


def execute():
    try:
        import edgy.project
    except ImportError as exc:
        raise ImportError(
            'You must install "edgy.project" to use this command.\n\n $ pip install edgy.project\n'
        ) from exc

    from edgy.project.__main__ import handle_init

    return handle_init(os.path.join(os.getcwd(), 'Projectfile'))


def register(parser):
    return execute
