import os

def execute(name, branch, overwrite_if_exists=False):
    try:
        from cookiecutter.main import cookiecutter
    except ImportError as exc:
        raise ImportError(
            'You must install "cookiecutter" to use this command.\n\n $ pip install cookiecutter\n'
        ) from exc

    if os.listdir(os.getcwd()) == []:
        overwrite_if_exists = True

    return cookiecutter(
        'https://github.com/python-bonobo/cookiecutter-bonobo.git',
        extra_context={'name': name},
        no_input=True,
        checkout=branch,
        overwrite_if_exists=overwrite_if_exists
    )


def register(parser):
    parser.add_argument('name')
    parser.add_argument('--branch', '-b', default='master')
    return execute
