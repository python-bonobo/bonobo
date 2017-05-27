import os


def execute(name):
    try:
        from cookiecutter.main import cookiecutter
    except ImportError as exc:
        raise ImportError(
            'You must install "cookiecutter" to use this command.\n\n $ pip install edgy.project\n'
        ) from exc

    return cookiecutter('https://github.com/python-bonobo/cookiecutter-bonobo.git', extra_context={'name': name}, no_input=True)


def register(parser):
    parser.add_argument('name')
    return execute
