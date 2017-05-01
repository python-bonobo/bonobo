import os


def execute():
    try:
        from edgy.project.__main__ import handle_init
    except ImportError as exc:
        raise ImportError(
            'You must install "edgy.project" to use this command.\n\n $ pip install edgy.project\n'
        ) from exc

    return handle_init(os.path.join(os.getcwd(), 'Projectfile'))


def register(parser):
    return execute
